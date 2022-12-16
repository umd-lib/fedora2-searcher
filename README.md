# fedora2-searcher

Python 3 Flask application to search Fedora2 / AdminTools; provides a backend searcher to a Bento Box style search
which expects a REST interface following the Quick Search model.

## Requires

* Python 3

### Running in Docker

```bash
$ docker build -t fedora2-searcher .
$ docker run -it --rm -p 5000:5000 --env-file=.env --read-only fedora2-searcher
```

### Building for Kubernetes

```bash
$ docker buildx build . --builder=kube -t docker.lib.umd.edu/fedora2-searcher:VERSION --push
```

### Endpoints

This will start the webapp listening on the default port 5000 on localhost
(127.0.0.1), and running in [Flask's debug mode].

Root endpoint (just returns `{status: ok}` to all requests):
<http://localhost:5000/>

/ping endpoint (just returns `{status: ok}` to all requests):
<http://localhost:5000/ping>

/search endpoint: `http://localhost:5000/search?q={query}&page={page number?}&per_page={results per page?}`

Example:

```bash
curl 'http://localhost:5000/search?q=kermit'
{
  "endpoint": "fedora2-search",
  "module_link": "https://digital.lib.umd.edu/resultsnew?query=kermit",
  "no_results_link": "https://digital.lib.umd.edu/resultsnew",
  "page": "0",
  "per_page": "3",
  "query": "kermit",
  "results": [
    {
      "description": "Young Jim Henson paints the finishing touches on Kermit the Frog, circa 1958.",
      "extra": {
        "collection": "University AlbUM",
        "htmlSnippet": [
          "Young Jim Henson puts finishing touches on <b>Kermit</b> the Frog, circa 1958"
        ],
        "thumbnail": "https://fedora.lib.umd.edu/fedora/get/umd:92324/umd-bdef:image/getThumbnail?maxHeight=110&maxWidth=110"
      },
      "item_format": "Image",
      "link": "https://digital.lib.umd.edu/resultsnew/id/umd%3A92323",
      "title": "Young Jim Henson puts finishing touches on Kermit the Frog, circa 1958"
    },
    {
      "description": "Jim Henson with Kermit and Sweetums, two of his Muppets, at a University of Maryland football game, November 3, 1979.",
      "extra": {
        "collection": "University AlbUM",
        "htmlSnippet": [
          "Jim Henson with <b>Kermit</b> and Sweetums, University of Maryland, November 3, 1979"
        ],
        "thumbnail": "https://fedora.lib.umd.edu/fedora/get/umd:6065/umd-bdef:image/getThumbnail?maxHeight=110&maxWidth=110"
      },
      "item_format": "Image",
      "link": "https://digital.lib.umd.edu/resultsnew/id/umd%3A6064",
      "title": "Jim Henson with Kermit and Sweetums, University of Maryland, November 3, 1979"
    },
    {
      "description": "Kermit and Miss Piggy at October 13, 1990 Homecoming Henson Tribute.",
      "extra": {
        "collection": "University AlbUM",
        "htmlSnippet": [
          "<b>Kermit</b> and Miss Piggy at 1990 Homecoming Henson Tribute"
        ],
        "thumbnail": "https://fedora.lib.umd.edu/fedora/get/umd:465957/umd-bdef:image/getThumbnail?maxHeight=110&maxWidth=110"
      },
      "item_format": "Image",
      "link": "https://digital.lib.umd.edu/resultsnew/id/umd%3A465956",
      "title": "Kermit and Miss Piggy at 1990 Homecoming Henson Tribute"
    }
  ],
  "total": 42
}
```

[Flask's debug mode]: https://flask.palletsprojects.com/en/2.2.x/cli/?highlight=debug%20mode

## License

See the [LICENSE](LICENSE.txt) file for license rights and limitations.
