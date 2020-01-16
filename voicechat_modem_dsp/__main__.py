from cleo import Application

from .cli.command_objects import TxFile, RxFile

app=Application(name="voicechat_modem_dsp")

app.add(TxFile())
app.add(RxFile())

if __name__=="__main__":
    app.run()