import parser.commandLineParser
import parser.svnRepositoryParser
import output.execution


def main():
    arguments = parser.commandLineParser.parse()

    output.execution.execute(arguments)
