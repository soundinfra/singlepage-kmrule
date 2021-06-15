# Single Web Page ([kmrule.com](https://kmrule.com))
This repository is an example of a single web page, powered by
[Sound//Infra](https://soundinfra.com).

[kmrule.com](https://kmrule.com) has some images, text, CSS, and even some
JavaScript to make it interactive. But the main thing that this repository shows
is just how easy it is to make changes to a web page that is powered by
<span style="font-family: monospace">Sound//Infra</span>.

The web is made up of *resources*, each with
a [URL](https://en.wikipedia.org/wiki/URL), or web address,
like `https://kmrule.com/index.html`. When you click on a link in your browser,
you get taken to a URL.

# Add or update a resource
To upload, or publish a resource to your domain, you just need to do
a `HTTP PUT` request. One way to do this is with the `curl` command, which is
installed on most systems:
```
me@host> curl -X PUT  \
 > -H "Authorization: Bearer $SOUNDINFRA_TOKEN" \
 > -H "Content-Type:" \
 > --data-binary "@public/index.html" \
 > https://kmrule.com/index.html
1ee1e6f4c99a61af0e718560785569cc,index.html
me@host>
```
A quick rundown of what's happening above:

* The `Authorization` header with your secret token is how
  <span style="font-family: monospace">Sound//Infra</span> ensures that only you can make changes
  to your domain. Without that token, an `Unauthorized` or `Forbidden` response
  will be returned. Just remember not to share that token with anybody else!
* Setting `Content-Type:` stops the `curl` command from using it's (incorrect)
  default content type. <span style="font-family: monospace">Sound//Infra</span>
  will automatically guess the content type based on common file extension
  (`.html` will be `text/html`), or you can manually set the content type.
* `--data-binary` tells the `curl` command to upload the contents of the file
  `public/index.html`
* Last but not least is the URL `https://kmrule.com/index.html` where the
  file you uploaded will be published to the web.
The response `1ee1e6f4c99a61af0e718560785569cc,index.html` is the MD5 hash,
and path of the file you uploaded.

### Check that your file was uploaded correctly
The first way to check that your file was uploaded correctly is to visit
[https://kmrule.com/index.html](https://kmrule.com/index.html) in your browser.
The path `index.html` is special, so you can also visit
[https://kmrule.com](https://kmrule.com).

#### Check the hash of the file
The second way to check your file was uploaded correctly is to check hash of
your local file against what
<span style="font-family: monospace">Sound//Infra</span> returned . You can use
the `md5sum` `md5` or `openssl md5` commands:
```
# Works on Linux and some Macs
me@host> md5sum public/index.html
1ee1e6f4c99a61af0e718560785569cc  public/index.html

# Works on Macs:
me@host> md5 public/index.html
MD5 (public/index.html) = 1ee1e6f4c99a61af0e718560785569cc

# Works if you have openssl installed
me@host> openssl md5 public/index.html
MD5(public/index.html)= 1ee1e6f4c99a61af0e718560785569cc
```
## See what is currently published to your domain
To check what is currently published to your domain, make a HTTP OPTIONS
request to your domain:
```
me@host> SOUNDINFRA_TOKEN=[... secret token ...]
me@host> curl -X OPTIONS \
 > -H "Authorization: Bearer $SOUNDINFRA_TOKEN" \
 > https://kmrule.com
 5f25c9509a9add571f5c75f2b1b41e93,error.html
 904d7bfb6107e74ae0469d06009e1250,images/fig_01_The_Pyrmont_Pad-full.png
   ... more resources ...
   ... in alphabetical order ...
 1ee1e6f4c99a61af0e718560785569cc,index.html
me@host>
```

<span style="font-family: monospace">Sound//Infra</span> will return the MD5
hash, and path of every resource on your domain (in alphabetical order, up to
1000 files).

## Delete a resource
You can delete resources with a HTTP DELETE request, like so:
```
me@host> curl -X DELETE -H "Authorization: Bearer $SOUNDINFRA_TOKEN" \
> https://kmrule.com/foo.html
me@host>
```
Note that this request succeeds *even if* the resource didn't exist in the
first place.

Also, it's worth pointing out that while it's easy to delete a resource with
<span style="font-family: monospace">Sound//Infra</span>, once you publish
something to the web, other people, and web pages may link to that resource. So
by deleting it, you may break those links. Additionally, people, and machines,
like search engines may download that resource and save it forever. Think of the
web as a place you want to publish things that will be available *forever*.

## Summary
Using only the `curl` command, we were able to update, check, and delete
resources from `https://kmrule.com`.

We are working on ways  to make it easier to publish your documents, photos,
and other content to the web, so stay tuned, this is just the beginning!