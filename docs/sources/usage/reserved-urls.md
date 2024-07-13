# Reserved URL 

When publishing posts, we get a URL assigned per post. With reserved URLs you can get multiple URLs all pointing to the same webpage.

## What are Reserved URLs used for?

Consider the following scenario: 

Your event website held it's first hot dog eating contest in 2022. Now following its success, you are making this event an annual occurrence. Your website sent press a promotional page with the title and URL - 
`https://mysite.com/hotdog-comp-2022`

You want to follow the same steps with a page for the 2023 event. Ideally the URL being sent
`https://mysite.com/hotdog-comp-2023"

Some decisions are growing with regards to managing your blog. Mainly, what happens to the older competition URL? 

First option to address this problem is to copy and paste pages since they have similar content, albeit the setback will be more pages to manage. 

Option two is to change the URL with the trailing year from `2022` to `2023`. However, those people whom bookmarked your previous page are facing a 404 when they try to revisit a `2022` link. 

Reserved URLs are introduced to combat these problems. Your event website posts can exculsively reserve a URL without neediing to copy and paste multiple pages. Following the fictional story we set out, the authors can now update the original contest page and then reserve the older URLs alongside. 


## Create a reserve URL

### From the Admin panel

To associate a blog post with a URL you must enter edit view from the admin portal. The software constrains you from setting reserved URLs on a post that in it's first time creation phase. More simply, reserved URL option will appear after the first save. 

1. Go to the admin panel
2. Click "Posts" in the sidebar
3. Chose the post you are planning to change
4. Reserved URLs are in the meta options near the bottom of edit post, navigate there 
5. Press the link "add another url" with plus symbol

At this point, the browser will open a new page. You should see a form with options for the reserve URL.

1. Select your site from the dropdown or create one
2. Type path you want to reserve for a post under `old path`
3. Bew path should be filled-out already, if not insert the post slug here
4. Select a match pattern, `Exact`, `Prefix`, `Regex`
4. Select a redirect type, this is related to internet fluency [more info about HTTP status codes](https://wikiless.org/wiki/List_of_HTTP_status_codes?lang=en#3xx_redirection)
5. Finally save

### From the Python API 

It is also possible to create new reserved URLs through the Django shell.

This example creates a reserved url with a 301 Moved Permanently redirect status response code.
```
>>> from django.conf import settings
>>> from django.contrib.redirects.models import Redirect
>>> # Add a new redirect.
>>> reserved_url = Redirect.objects.create(
	site_id=1,
	old_path="online-shopping",
	new_path="shop",
	type_status_code=Redirect.TYPE_301
)
>>> reserved_url.save()
>> reserved_url
```
