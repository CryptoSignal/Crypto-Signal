""" Handles outputting results to the terminal.
"""

import json

import structlog


class Output():
    """ Handles outputting results to the terminal.
    """

    def __init__(self):
        """Initializes Output class.
        """

        self.logger = structlog.get_logger()
        self.dispatcher = {
            'cli': self.to_cli,
            'csv': self.to_csv,
            'json': self.to_json
        }


    def to_cli(self, results, market_pair):
        """Creates the message to output to the CLI

        Args:
            market_pair (str): Market pair that this message relates to.
            results (dict): The result of the completed analysis to output.

        Returns:
            str: Completed cli message
        """

        normal_colour = '\u001b[0m'
        hot_colour = '\u001b[31m'
        cold_colour = '\u001b[36m'

        output = "{}:\t\n".format(market_pair)
        for indicator_type in results:
            output += '\n{}:\t'.format(indicator_type)
            for indicator in results[indicator_type]:
                for i, analysis in enumerate(results[indicator_type][indicator]):
                    colour_code = normal_colour

                    if 'is_hot' in analysis['result'].iloc[-1]:
                        if analysis['result'].iloc[-1]['is_hot']:
                            colour_code = hot_colour

                    if 'is_cold' in analysis['result'].iloc[-1]:
                        if analysis['result'].iloc[-1]['is_cold']:
                            colour_code = cold_colour

                    formatted_values = list()
                    if 'signal' in analysis['config']:
                        for signal in analysis['config']['signal']:
                            value = analysis['result'].iloc[-1][signal]
                            if isinstance(value, float):
                                formatted_values.append(format(value, '.8f'))
                            else:
                                formatted_values.append(value)
                            formatted_string = '/'.join(formatted_values)

                        output += "{}{}: {}{} \t".format(
                            colour_code,
                            '{} #{}'.format(indicator, i),
                            formatted_string,
                            normal_colour
                        )

                    if 'key_signal' in analysis['config'] and 'crossed_signal' in analysis['config']:
                        key_value = analysis['result'].iloc[-1][analysis['config']['key_signal']]
                        crossed_value = analysis['result'].iloc[-1][analysis['config']['crossed_signal']]
                        if isinstance(key_value, float):
                            key_value = format(key_value, '.8f')

                        if isinstance(crossed_value, float):
                            crossed_value = format(crossed_value, '.8f')

                        formatted_string = '{}/{}'.format(key_value, crossed_value)
                        output += "{}{}: {}{} \t".format(
                            colour_code,
                            '{} #{}'.format(indicator, i),
                            formatted_string,
                            normal_colour
                        )

        output += '\n\n'
        return output


    def to_csv(self, results, market_pair):
        """Creates the csv to output to the CLI

        Args:
            market_pair (str): Market pair that this message relates to.
            results (dict): The result of the completed analysis to output.

        Returns:
            str: Completed CSV message
        """

        output = str()
        for indicator_type in results:
            for indicator in results[indicator_type]:
                for i, analysis in enumerate(results[indicator_type][indicator]):
                    for signal in analysis['config']['signal']:
                        value = analysis['result'].iloc[-1][signal]
                        if isinstance(value, float):
                            value = format(value, '.8f')

                        is_hot = str()
                        if 'is_hot' in analysis['result'].iloc[-1]:
                            is_hot = str(analysis['result'].iloc[-1]['is_hot'])

                        is_cold = str()
                        if 'is_cold' in analysis['result'].iloc[-1]:
                            is_cold = str(analysis['result'].iloc[-1]['is_cold'])

                        new_output = ','.join([
                            market_pair,
                            indicator,
                            str(i),
                            value,
                            is_hot,
                            is_cold
                        ])

                        output += '\n{}'.format(new_output)

        return output


    def to_json(self, results, market_pair):
        """Creates the JSON to output to the CLI

        Args:
            market_pair (str): Market pair that this message relates to.
            results (dict): The result of the completed analysis to output.

        Returns:
            str: Completed JSON message
        """

        result_list = list()
        for indicator_type in results:
            for indicator in results[indicator_type]:
                for analysis in results[indicator_type][indicator]:
                    result_list.append(analysis['result'].to_dict(orient='records')[-1])

        output = {'pair': market_pair, indicator_type: result_list}
        output = json.dumps(output)
        output += '\n'
        return output
