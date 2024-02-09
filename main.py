import parser.commandLineParser
import parser.svnRepositoryParser
import output.execution
import data.configuration as configuration


def main():
    arguments = parser.commandLineParser.parse()

    data_dict = parser.svnRepositoryParser.parse(configuration.remote_url)

    output.execution.execute(arguments, data_dict)
