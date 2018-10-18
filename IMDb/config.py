###
# Copyright (c) 2012, Dan
# All rights reserved.
#
#
###

import supybot.conf as conf
import supybot.registry as registry
import supybot.ircutils as ircutils

def configure(advanced):
    # This will be called by supybot to configure this module.  advanced is
    # a bool that specifies whether the user identified himself as an advanced
    # user or not.  You should effect your configuration by manipulating the
    # registry as appropriate.
    from supybot.questions import expect, anything, something, yn
    conf.registerPlugin('IMDb', True)


IMDb = conf.registerPlugin('IMDb')
# This is where your configuration variables (if any) should go.  For example:
# conf.registerGlobalValue(IMDb, 'someConfigVariableName',
#     registry.Boolean(False, """Help for someConfigVariableName."""))

conf.registerGroup(IMDb, 'formats')

conf.registerChannelValue(IMDb, 'shortoutputorder',
        registry.String('title,runtime,rating,url',
            'Order that parts will be output. ; is line separator and , is field separator'))

conf.registerChannelValue(IMDb, 'outputorder',
        registry.String('title,runtime,rating,url;description,genres,keywords',
            'Order that parts will be output. ; is line separator and , is field separator'))

conf.registerChannelValue(IMDb, 'fulloutputorder',
        registry.String('title,url;runtime,rating;description;director,creator,actor;genres,keywords',
            'Order that parts will be output. ; is line separator and , is field separator'))

conf.registerChannelValue(IMDb.formats, 'url',
        registry.String('%(url)s', 'Format for the output of imdb command'))

conf.registerChannelValue(IMDb.formats, 'title',
        registry.String(ircutils.bold('%(title)s'), 'Format for the output of imdb command'))

conf.registerChannelValue(IMDb.formats, 'description',
        registry.String(ircutils.bold('Description:') + '  %(description)s', 'Format for the output of imdb command'))

conf.registerChannelValue(IMDb.formats, 'creator',
        registry.String(ircutils.bold('Creator:') + '  %(creator)s', 'Format for the output of imdb command'))

conf.registerChannelValue(IMDb.formats, 'director',
        registry.String(ircutils.bold('Director:') + ' %(director)s', 'Format for the output of imdb command'))

conf.registerChannelValue(IMDb.formats, 'actor',
        registry.String(ircutils.bold('Actors:') + ' %(actor)s', 'Format for the output of imdb command'))

conf.registerChannelValue(IMDb.formats, 'genres',
        registry.String(ircutils.bold('Genres:') + ' %(genres)s', 'Format for the output of imdb command'))

conf.registerChannelValue(IMDb.formats, 'keywords',
        registry.String(ircutils.bold('Keywords:') + ' %(keywords)s', 'Format for the output of imdb command'))

conf.registerChannelValue(IMDb.formats, 'runtime',
        registry.String(ircutils.bold('Runtime:') + ' %(runtime)s', 'Format for the output of imdb command'))

conf.registerChannelValue(IMDb.formats, 'language',
        registry.String(ircutils.bold('Language:') + ' %(language)s', 'Format for the output of imdb command'))

conf.registerChannelValue(IMDb.formats, 'rating',
        registry.String(ircutils.bold('Content Rating:') + ' %(contentRating)s ' + ircutils.bold('IMDb:') + ' %(rating)s/10 (%(ratingCount)s votes) ' + ircutils.bold('Metacritic:') + ' %(metascore)s/100', 'Format for the output of imdb command'))

# vim:set shiftwidth=4 tabstop=4 expandtab:
