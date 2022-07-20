# redirect-rules-testing

Small python script to test redirects.

The following options are currently integrated:

- check the return code
- check whether a redirection is desired
- check the content_type
- check the redirection location

## Examples

```yaml
---

redirects:

  - source: https://www.boone-schulz.de/?side=ueber&display=archiv&artikel=3x-ie-unter-linux--wo-gibts-denn-sowas%253Fside%3Dartikel
    expected:
      return_code: 200
      redirection: false
      content_type: "text/html"

  - source: https://www.boone-schulz.de/?side=ueber&display=archiv&artikel=3x-ie-unter-linux--wo-gibts-denn-sowas%253Fside%3Dartikel
    expected:
      return_code: 404
      content_type: text/html

  - source: http://www.boone-schulz.de/tags
    expected:
      return_code: 200
      location: https://www.boone-schulz.de/tags/

```

## output

```bash
OKAY : request 'https://www.boone-schulz.de/?side=ueber&display=archiv&artikel=3x-ie-unter-linux--wo-gibts-denn-sowas%253Fside%3Dartikel'
ERROR: request 'https://www.boone-schulz.de/?side=ueber&display=archiv&artikel=3x-ie-unter-linux--wo-gibts-denn-sowas%253Fside%3Dartikel' needs test
   wrong return_code! get '200', but expected '404'
{
  "url": "https://www.boone-schulz.de/?side=ueber&display=archiv&artikel=3x-ie-unter-linux--wo-gibts-denn-sowas%253Fside%3Dartikel",
  "code": 200,
  "content_type": "text/html"
}
OKAY : request 'http://www.boone-schulz.de/tags' - redirect count 2
```
