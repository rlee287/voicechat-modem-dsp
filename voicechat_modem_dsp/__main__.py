from cleo import Application

from .cli.command_objects import TxFile

app=Application(name="voicechat_modem_dsp")

app.add(TxFile())

if __name__=="__main__":
    app.run()