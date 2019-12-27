import cleo

import os

class TxFile(cleo.Command):
    """
    Modulates a given datafile and saves modulated audio to an audio file

    transmit_file
        {filename : Data file to modulate}
        {--o|output=modulated.wav : Output audio file }
        {--config= : Configuration file} 
    """

    def handle(self):
        config_file_name=self.option("config")
        output_file_name=self.option("output")
        self.line("Test base command")
        if not config_file_name or not os.path.isfile(config_file_name):
            self.line_error("A valid configuration file must be specified.",
                "error")
            return 1

        if os.path.exists(output_file_name):
            if os.path.isdir(output_file_name):
                self.line_error("Output file {} must be writable as a file."
                    .format(output_file_name),"error")
                return 1

            if self._io.is_interactive():
                result=self.confirm("Output file {} already exists. Overwrite?"
                    .format(output_file_name))
                self.line(str(result))
            else:
                self.line_error("Output file {} already exists "
                    "and program is in noninteractive mode."
                    .format(output_file_name),"error")
                return 1
