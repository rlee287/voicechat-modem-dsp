from cleo import Application

from .cli.command_objects import TxFile

app=Application()

app.add(TxFile())

if __name__=="__main__":
    app.run()