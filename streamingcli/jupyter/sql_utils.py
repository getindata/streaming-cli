
def inline_sql_in_cell(cell_contents) -> str:
    """
    Converts cell contents to a single line SQL statement.
    """
    return cell_contents.replace('\n', ' ')


def is_dml(sql: str) -> bool:
    valid_dml_statements = ['insert', 'update', 'delete', 'lock', 'call', 'explain']
    for dml in valid_dml_statements:
        if dml in sql.lower():
            return True
    return False
