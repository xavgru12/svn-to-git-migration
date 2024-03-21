import data.configuration as configuration
import parser.commandLineParser
import parser.svnRepositoryParser
import output.execution


def main():
    arguments = parser.commandLineParser.parse()

    data_dict = parser.svnRepositoryParser.parse(configuration.get_remote_url())

    output.execution.execute(arguments, data_dict)
