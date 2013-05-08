from twisted.internet import reactor
from twisted.internet.ssl import ClientContextFactory
from twisted.web.client import HTTPClientFactory

from commandant.commands import TwistedCommand


class cmd_get_page(TwistedCommand):
    """Download a web page using Twisted and print it to the screen.

    This command uses Twisted to download a web page and demonstrates how to
    write an asynchronous command with Commandant.
    """

    takes_args = ["url"]

    def run(self, url):
        """Fetch the page at C{url} and print it to the screen."""
        client = HTTPClientFactory(url)
        if client.scheme == "https":
            factory = ClientContextFactory()
            reactor.connectSSL(client.host, client.port, client, factory)
        else:
            reactor.connectTCP(client.host, client.port, client)

        def write_response(self, result):
            print >>self.outf, result.decode("utf-8")

        def write_failure(self, failure):
            print >>self.outf, failure

        client.deferred.addCallback(write_response)
        client.deferred.addErrback(write_failure)
        return client.deferred
