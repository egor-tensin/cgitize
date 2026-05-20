# Copyright (c) 2026 Egor Tensin <egor@tensin.name>
# This file is part of the "cgitize" project.
# For details, see https://github.com/egor-tensin/cgitize.
# Distributed under the MIT License.


def update(path, success, error=None):
    with open(path, 'w') as file:
        contents = ''
        if not success:
            contents = (
                '''<p style="text-align: center; color: red; font-weight: bold;">'''
            )
            contents += '''Some repositories couldn't be updated, please check application logs for details.'''
            if error is not None:
                contents += f'''<br>{type(error).__name__}: {error}'''
            contents += '''</p>\n'''
        file.write(contents)
