import gspread
from datetime import datetime
import json
import copy

scope = [
    "https://spreadsheets.google.com/feeds​",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file​",
    "https://www.googleapis.com/auth/drive​",
]

colorCell = "L2"

try:
    settings_file = open("settings.json")
except Exception as e:
    print(e)
    print(
        "Could not find settings.json, make sure you have the file in the same directory as the exe, and named exactly 'settings.json'"
    )
    wait = input("")

settings = json.load(settings_file)
settings_file.close()
try:
    gc = gspread.service_account(filename="credentials.json")
except Exception as e:
    print(e)
    print(
        "Could not find credentials.json, make sure you have the file in the same directory as the exe, and named exactly 'credentials.json'"
    )
    wait = input("")


while True:
    try:
        sh = gc.open_by_url(settings["spreadsheet-link"])
    except:
        creds_file = open("credentials.json", "r")
        creds = json.load(creds_file)
        creds_file.close()
        print("Don't forget to share the google sheet with", creds["client_email"])
        settings["spreadsheet-link"] = input("Link to your Sheet:")
        settings_file = open("settings.json", "w")
        json.dump(settings, settings_file)
        settings_file.close()
        continue
    else:
        break

dataSheet = sh.worksheet("Raw Data")
statsSheet = sh.worksheet("Stats")
color = (15.0, 15.0, 15.0)
if statsSheet.get(colorCell)[0][0] == "Gray":
    statsSheet.update(colorCell, "White")
    color = (1.0, 1.0, 1.0)
else:
    statsSheet.update(colorCell, "Gray")
pushedLines = 0
cfgStartCol = "A"
cfgStartRow = 6
columns = int(statsSheet.get("B2")[0][0])
rows = int(statsSheet.get("B3")[0][0])
pushCol = statsSheet.get("D2")[0][0]
pushRow = statsSheet.get("D3")[0][0]
config = statsSheet.get(
    cfgStartCol
    + str(cfgStartRow)
    + ":"
    + chr(ord(cfgStartCol) + columns - 1)
    + str(cfgStartRow + rows - 1),
    value_render_option="FORMULA",
)


def push_data(data):
    global pushedLines
    if data != None:
        print(data)
        dataSheet.insert_rows(
            [[str(datetime.now())] + data],
            row=2,
            value_input_option="USER_ENTERED",
        )

        endColumn = ord("A") + len(data)
        endColumn1 = ord("A") + (endColumn // ord("A")) - 1
        endColumn2 = ord("A") + ((endColumn - ord("A")) % 26)
        endColumn = chr(endColumn1) + chr(endColumn2)
        pushedLines += 1
    else:
        print("Data was empty didn't push")
    if pushedLines == 1:
        dataSheet.format(
            "A2:" + endColumn + "2",
            {
                "backgroundColor": {
                    "red": color[0],
                    "green": color[1],
                    "blue": color[2],
                }
            },
        )
    update_session()
    # print("done")


def get_sec(time_str):
    """Get Seconds from time."""
    h, m, s = time_str.split(":")
    return float(int(h) * 3600 + int(m) * 60 + int(s))


def initialize_session():
    cfgStartCol = "A"

    cfgStartRow = 6
    columns = int(statsSheet.get("B2")[0][0])
    rows = int(statsSheet.get("B3")[0][0])
    pushCol = statsSheet.get("D2")[0][0]
    pushRow = statsSheet.get("D3")[0][0]

    init_config = getConfig(cell_list=False)

    statsSheet.insert_row([""], index=int(pushRow))
    statsSheet.insert_rows(
        init_config, row=int(pushRow), value_input_option="USER_ENTERED"
    )

    gc.request(
        "post",
        "https://sheets.googleapis.com/v4/spreadsheets/" + sh.id + ":batchUpdate",
        json={
            "requests": [
                {
                    "copyPaste": {
                        "source": {
                            "sheetId": statsSheet.id,
                            "startRowIndex": cfgStartRow - 1,
                            "endRowIndex": cfgStartRow + rows - 1,
                            "startColumnIndex": ord(cfgStartCol) - ord("A"),
                            "endColumnIndex": ord(cfgStartCol) - ord("A") + columns,
                        },
                        "destination": {
                            "sheetId": statsSheet.id,
                            "startRowIndex": int(pushRow) - 1,
                            "endRowIndex": int(pushRow) + rows - 1,
                            "startColumnIndex": ord(pushCol) - ord("A"),
                            "endColumnIndex": ord(pushCol) - ord("A") + columns,
                        },
                        "pasteType": "PASTE_FORMAT",
                        "pasteOrientation": "NORMAL",
                    }
                }
            ]
        },
    )


def update_session():
    cell_list = getConfig()
    statsSheet.update_cells(cell_list, value_input_option="USER_ENTERED")


def getConfig(cell_list=True):
    if cell_list:
        result = statsSheet.range(
            pushCol
            + str(pushRow)
            + ":"
            + chr(ord(pushCol) + columns - 1)
            + str(int(pushRow) + rows - 1)
        )
    else:
        result = copy.deepcopy(config)

    config_copy = copy.deepcopy(config)
    config_copy[0][0].replace("~", str(1 + pushedLines)).replace("'=", "=")
    for i in range(len(config_copy)):
        for j in range(len(config_copy[i])):
            if type(config_copy[i][j] == str):
                if cell_list:
                    result[(i * columns) + j].value = (
                        config_copy[i][j]
                        .replace("~", str(1 + pushedLines))
                        .replace("'=", "=")
                    )
                else:
                    result[i][j] = (
                        config_copy[i][j]
                        .replace("~", str(1 + pushedLines))
                        .replace("'=", "=")
                    )
    return result
