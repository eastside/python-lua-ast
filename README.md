# lua-ast

This is very simple, incomplete and  minimal implementation of lua parser/printer in Python. I've written it to parse and modify Prosody (a xmpp server) configuration file, so you can find here implementation which handles language constructs usualy present in Prosody config (assignments, tables, function calls, booleans and strings). Just take a look into `tests.py` to see what is implemented.

Current version of parser is based on this BNF specification: https://www.lua.org/manual/5.3/manual.html#9 (you can find it also in this repo: grammar.txt).

## Contributions

If you want to parse something more with this library, please provide pull request with:

    * parser implementation

    * printer implementation

    * appropriate tests cases


## Bugs

If you have found any inconsistency or bug, please create an issue on this projects github bug tracker.
