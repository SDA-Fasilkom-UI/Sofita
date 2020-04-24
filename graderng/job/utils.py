import concurrent.futures
import io
import os
import zipfile

from bs4 import BeautifulSoup

from app.proxy_socket import ProxySocket
from app.proxy_requests import ProxyRequests


class MossUploader():
    """
    Copied and edited from:
    https://github.com/soachishti/moss.py/blob/master/mosspy/moss.py
    """

    languages = (
        "c", "cc", "java", "ml", "pascal", "ada",
        "lisp", "scheme", "haskell", "fortran", "ascii", "vhdl",
        "verilog", "perl", "matlab", "python", "mips", "prolog",
        "spice", "vb", "csharp", "modula2", "a8086", "javascript",
        "plsql"
    )
    server = 'moss.stanford.edu'
    port = 7690

    def __init__(self, user_id, language="c"):
        self.user_id = user_id
        self.options = {
            "l": "c",  # lang
            "m": 10,   # limit
            "d": 0,    # directory mode
            "x": 0,    # experimental server
            "c": "",   # comment
            "n": 250   # number of matching files
        }
        self.base_files = []
        self.files = []

        if language in self.languages:
            self.options["l"] = language

    def _sanitize_display_name(self, display_name):
        return display_name.replace(" ", "_")

    def add_base_file_from_string(self, content, display_name):
        display_name = self._sanitize_display_name(display_name)
        if len(content) > 0:
            self.base_files.append((content, display_name))

    def add_file_from_string(self, content, display_name):
        display_name = self._sanitize_display_name(display_name)
        if len(content) > 0:
            self.files.append((content, display_name))

    def upload_file(self, s, content, display_name, file_id):
        message = "file {0} {1} {2} {3}\n".format(
            file_id,
            self.options['l'],
            len(content.encode()),
            display_name
        )
        s.send(message.encode())
        s.send(content.encode())

    def send(self):
        s = ProxySocket.socket()
        s.connect((self.server, self.port))

        s.send("moss {}\n".format(self.user_id).encode())
        s.send("directory {}\n".format(self.options['d']).encode())
        s.send("X {}\n".format(self.options['x']).encode())
        s.send("maxmatches {}\n".format(self.options['m']).encode())
        s.send("show {}\n".format(self.options['n']).encode())

        s.send("language {}\n".format(self.options['l']).encode())
        recv = s.recv(1024)
        if recv == "no":
            s.send(b"end\n")
            s.close()
            raise Exception("send() => Language not accepted by server")

        for content, display_name in self.base_files:
            self.upload_file(s, content, display_name, 0)

        index = 1
        for content, display_name in self.files:
            self.upload_file(s, content, display_name, index)
            index += 1

        s.send("query 0 {}\n".format(self.options['c']).encode())

        response = s.recv(1024)

        s.send(b"end\n")
        s.close()

        return response.decode().replace("\n", "")


class MossDownloader():
    """
    Copied and edited from:
    https://github.com/soachishti/moss.py/blob/master/mosspy/download_report.py
    """

    def process_url(self, url, base_url):
        r = ProxyRequests.get(url)
        r.raise_for_status()

        soup = BeautifulSoup(r.text, 'lxml')
        filename = os.path.basename(url)

        # Not file name eg. 123456789 or is None
        if not filename or len(filename.split(".")) == 1:
            filename = "index.html"

        urls = []
        for more_url in soup.find_all(['a', 'frame']):
            if more_url.has_attr('href'):
                link = more_url.get('href')
            else:
                link = more_url.get('src')

            if link and (link.find("match") != -1):  # Download only results urls
                link_fragments = link.split('#')
                link = link_fragments[0]  # remove fragment from url

                link_hash = ""
                if len(link_fragments) > 1:
                    link_hash = "#" + link_fragments[1]

                basename = os.path.basename(link)

                if basename == link:  # Handling relative urls
                    link = base_url + basename

                if more_url.name == "a":
                    more_url['href'] = basename + link_hash
                elif more_url.name == "frame":
                    more_url['src'] = basename

                urls.append(link)

        return (filename, str(soup), urls)

    def download_and_zip_report(self, url):

        if len(url) == 0:
            raise Exception("Empty url supplied")

        base_url = url + "/"

        buf = io.BytesIO()
        zf = zipfile.ZipFile(buf, "a", zipfile.ZIP_DEFLATED, False)

        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            processed_urls = set([url])
            curr_futures = [executor.submit(self.process_url, url, base_url)]
            next_futures = []

            while len(curr_futures) > 0:
                for future in concurrent.futures.as_completed(curr_futures):

                    filename, content, urls = future.result()
                    zf.writestr(filename, content)

                    for url in urls:
                        if url not in processed_urls:
                            processed_urls.add(url)
                            next_futures.append(executor.submit(
                                self.process_url, url, base_url)
                            )

                curr_futures = next_futures
                next_futures = []

        zf.close()
        return buf
