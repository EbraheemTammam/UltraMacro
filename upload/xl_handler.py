import pandas as pd
from io import BytesIO



pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)

LEVELS = {'الاول': 1, 'الأول': 1, 'الثاني': 2, 'الثانى': 2, 'الثالث': 3, 'الرابع': 4}
SEMESTERS = {'الاول': 1, 'الأول': 1, 'الثاني': 2, 'الثانى': 2, 'الصيفي': 3, 'الصيفى': 3}
DEPARTMENTS = {
    None: None,
    'فيزياء': 'Physics',
    'فيزياء عامة': 'Physics',
    'فيزياء عامه': 'Physics',
    'الفيزياء': 'Physics',
    'الكيمياء': 'Chemistry',
    'Chemistry': 'Chemistry',
    'الرياضيات': 'Mathematics',
    'Mathematics': 'Mathematics',
    'النبات': 'Botany',
    'Botany': 'Botany',
    'علم الحيوان': 'Zoology',
    'Zoology': 'Zoology',
    'الجيولوجيا': 'Geology',
    'Geology':'Geology',
}

#   getting actual content of the excel sheet
async def drop_empty_axes(df: pd.DataFrame) -> pd.DataFrame:
    df = df.dropna(how = 'all')
    df = df.dropna(axis = 1, how = 'all')
    return df


#   get just the cells that not null
async def advanced_cleanup(df: pd.DataFrame) -> pd.DataFrame:
    return df[df.notna()]

#   get header data
async def get_header_data(df: pd.DataFrame) -> pd.DataFrame:
    year = await advanced_cleanup(df.iloc[0])
    year = year.iloc[0].split('-')[1]
    cell = await advanced_cleanup(df.iloc[1])
    cell = cell.iloc[0].split('-')
    regulation = cell[0].strip()
    level = LEVELS.get(cell[1].split()[1])
    semester = SEMESTERS.get(cell[2].split()[2]) if len(cell[2].split()) > 2 else None  
    month = cell[3][1:]
    division = await advanced_cleanup(df.iloc[2])
    division = division.iloc[0].split(' : ')[1]
    department = None
    if '/' in division:
        division = [d.strip() for d in division.split('/')]
        department = division[-2] if len(division) < 4 else division[-3]
        division = division[-1] if len(division) < 4 else '/'.join(division[-2:])
    return {
        'regulation': regulation,
        'year'      : year,
        'level'     : int(level) if level else None,
        'semester'  : int(semester),
        'month'     : month,
        'department': DEPARTMENTS[department],
        'division'  : division.replace(
            '-', '/', 1
            ).replace(
            'ه', 'ة', 1
            ).replace(
            'الكيمياءعلم', 'الكيمياء/علم', 1
            ).replace(
            'الكيمياءالكيمياء', 'الكيمياء/الكيمياء', 1
            ).replace(
            'الكيمياءالنبات', 'الكيمياء/النبات', 1
            ).replace(
            'الكيمياءميكروبيولوجى', 'الكيمياء/ميكروبيولوجى', 1
            ).replace(
            'الكيمياءالجيولوجيا', 'الكيمياء/الجيولوجيا', 1
            ).replace(
            'الاحصاء', 'الإحصاء', 1
            )
    }

#   initial cleanup
async def initial_cleanup(df: pd.DataFrame) -> pd.DataFrame:
    #df = df.dropna(thresh = 2)
    df = df.iloc[7: -2] if len(await advanced_cleanup(df.iloc[-1])) == 2 else df.iloc[7: ]
    dropped = await drop_empty_axes(df)
    return dropped.iloc[: , 4: -1][df != ' ']

#	reforming the data
async def reform(df : pd.DataFrame) -> list:
    reformed = []
    r = 0
    while r < df.shape[0]:
        c = 0
        while c < df.shape[1] - 2:
            if pd.isnull(df.iloc[r, c]): 
                c += 3
                continue
            reformed.append(
                {
                    'seat_id'  : int(df.iloc[r, -1]), 
                    'student'  : df.iloc[r, -2], 
                    'course'   : df.iloc[r, c].replace(')', '', 1).replace('(', '', 1),
                    'code'     : df.iloc[r + 1, c][1: -1].upper().replace(' ', ''),
                    'hours'    : int(df.iloc[r + 2, c].split()[2]), 
                    'grade'    : df.iloc[r + 3, c], 
                    'points'   : float(df.iloc[r + 3, c + 1]), 
                    'mark'     : df.iloc[r + 3, c + 2],
                    'full_mark': int(df.iloc[r + 2, c].split()[0])
                }
            )    
            if reformed[-1]['mark'] in ['راسب', 'غـ', 'حر', 'رل']: reformed[-1]['mark'] = -1.0
            elif reformed[-1]['mark'] in ['ناجح', 'عذر']: reformed[-1]['mark'] = 0.0
            reformed[-1]['mark'] = float(reformed[-1]['mark'])
            c += 3
        r += 4
    return reformed

#   final dictionary
async def final_dict(file):
    xl_file = pd.ExcelFile(BytesIO(file))
    whole = []
    sheets = xl_file.sheet_names
    for sheet in sheets:
        file = pd.read_excel(xl_file, sheet_name=sheet)
        file = await drop_empty_axes(file)
        file = await initial_cleanup(file)
        whole += await reform(file)
    file = pd.read_excel(xl_file)
    file = await drop_empty_axes(file)
    file = file.iloc[:5]
    header_data = await get_header_data(file)
    #whole = [dict(i, **header_data) for i in whole]
    return {'headers': header_data, 'content': whole}

#   divisions file handling
async def extract_divisions(file):
    data = []
    file = pd.read_excel(file)
    for r in file.iterrows():
        departments = [v.strip() for v in r[1][0].split('+')]
        data.append(
            {
                'department_1_id': DEPARTMENTS[departments[0]],
                'department_2_id': DEPARTMENTS[departments[1]] if len(departments) > 1 else None,
                'name': r[1][1].strip(),
                'hours': int(r[1][2]),
                'private': bool(r[1][3]),
                'group': False
            }
        )
    return data

#   courses file handling
async def extract_courses(file):
    data = []
    file = pd.ExcelFile(file)
    file = pd.read_excel(file, sheet_name='ساعات معتمدة')
    for r in file.iterrows():
        data.append(
            {
                'level': int(r[1][0]),
                'semester': int(r[1][1]),
                'division': r[1][2].strip(),
                'code': str(r[1][3]).strip(),
                'required': True if r[1][5] == 1 else False,
                'name': r[1][6].strip(),
                'lecture_hours': r[1][7],
                'practical_hours': r[1][8],
                'credit_hours': r[1][9],
            }
        )
    return data
        
