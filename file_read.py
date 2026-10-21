import pandas

def unpack_list(pylist: list[any]) -> any: 
    """
    unpacks a list with 1 element.
    
    :param pylist: a list with any type

    :return: the first entry
    """
    if len(pylist) > 1: raise ValueError("List length have to be 1 to be unpacked.")
    return pylist[0]

def transpose(matrix: list[list]) -> list[list]:
    """
    Transpose a matrix

    :param matrix: a list[list] that has same length for each entry

    :return: list[list] transposed matrix
    """
    average_col_len = 0
    for i, lst in enumerate(matrix):
        average_col_len: float = (average_col_len * i + len(lst)) / (i + 1)
        if average_col_len != float(len(lst)): raise ValueError("Matrix have to be in uniform length.")

    return [list(row) for row in zip(*matrix)]
    
def extract_data(file_path: str, along_vertical: bool = False, ignore_header = False) -> list[list]:
    """
    opens up an excel path and read data

    :param along_vertical: True if the data aligns vertically

    :return: a list[list] containing the sheet data from the first row and column to the last row and column with data.
    """

    df = pandas.read_excel(file_path, header=None)
    sheet_data =  transpose([df[col].tolist() for col in df.columns]) if along_vertical else [df[col].tolist() for col in df.columns]

    return sheet_data[1:] if ignore_header else sheet_data