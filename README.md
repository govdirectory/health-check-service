# Govdirectory Health Check Service

Microservice that validates various external identifiers and URLs associated with a given Wikidata identifier. It comes with interactive documentation and a Docker container.

## How it works

When the service is given a Wikidata item, it looks up all the configured properties, and if statements using those are found it generates a URL for each value.

The service then goes through the URLs one by one and issues HTTP HEAD requests towards them. If the resulting HTTP status code is above 400 an error has occurred.

Lastly, the service returns a list of each error, so if no of the URLs raised an error, the service returns an empty list.

## Install

After having cloned or in other ways downloaded this repository, build and run your Docker image with the following commands:

```
docker build -t yourimage ./
docker run --name yourcontainer -p 80:80 yourimage
```

The service will now serve its documentation at `http://127.0.0.1/`.

## Configured properties

These properties are supported by default, but you can technically configure this service for any Wikidata properties that are either external identifiers with formatter URLs or properties which holds values with the datatype "URL".

### URL properties

 - official website (P856)
 - URL for citizen's initiatives (P9732)

### External identifier properties

 - Twitter username (P2002)
 - YouTube channel ID (P2397)
 - Facebook ID (P2013)
 - Instagram username (P2003)
 - GitHub username (P2037)
 - Vimeo identifier (P4015)
 - Flickr user ID (P3267)
 - Pinterest username (P3836)
 - Dailymotion channel ID (P2942)
 - TikTok username (P7085)
 - SlideShare username (P4016)

### Unsupported Properties/Platforms

Some platforms implement various technical barriers.

 - LinkedIn company ID (P4264) [Stackoverflow](https://stackoverflow.com/questions/27231113/999-error-code-on-head-request-to-linkedin)
