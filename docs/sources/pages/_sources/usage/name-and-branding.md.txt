# Name and branding 

Your website branding such as page titles and copyright signage, all appear with a placeholder - `example.com`. 

These options are customisable from the admin panel, under the banner of our Sites module. 

The items of interest are directly accessible from [http://127.0.0.1:8000/admin/sites/site/](http://127.0.0.1:8000/admin/sites/site/).

## Customise your site title
1. Open the admin portal
2. Click through to **Sites** > **example.com**
3. Specify your site using the form 
4. Finish by **Save**

The required fields are described as:

**Domain name**

The fully qualified domain name associated with the website. For example, www.example.com.

**Display name**

A human-readable “verbose” name for the website.

**ID**

ID, as an integer, of the current site in the Django site database table.

```{note}
Django knows the default site for your project from **SITE_ID** settings. So, if you do not specify a site, Django prefers value `1`. Check your settings.py files.
```

## Deleting example.com entry

Yes, you are free to delete the example object, however, you may encounter unexpected behavior as a result. Prefer editing the example entry instead. If you must delete, look at changing all references in the database and updating your `SITE_ID` settings.

You can identify a problem when **"No Title"** error appears on your pages. This error means a Site object does not exist and the SITE_ID is missing.

If you are experiencing a disruption after deleting the example name, you have some options to reverse the error.

Start by accessing the admin portal:
1. Open the admin portal
2. Click **Sites**
3. Proceed with **Add Site +**
4. Enter valid display and domain names
5. Save

The `ID` for each Site will be shown in the first column of the admin list and read-only field inside the form. These `ID` fields are what you need to use as SITE_ID:
```{image} ../_static/sites-id-admin-preview.png
:alt: Admin homepage, orange arrow denotes where the blog module is resides
:class: .screenshot
```
Once you have found what you are looking for, copy the numeric value into your `settings.py`, the original value is typically **SITE_ID=1**, perform an amendment and restart the server. 

## Managing multiple sites 

When posts are contextual in nature, then the blog relies on the Site module to serve different traffic. A single content store can be used on different domains too. For example, `DjangoNews.com`'s database drives `GamingDjango.com` for rows marked gaming.

### Brief history of Sites
Django was originally developed at a newspaper to publish content on multiple domains; using one single content base. There was a desire from the staff to associate articles with one or more sites and avoid duplication. 

This is where the Sites module comes in. Its purpose is to mark content to be displayed for different domains.

### Examples

The benefits of adding multiple sites is useful for other Django tools too. Think of Sites module as a way of describing any website as a stakeholder, even external domains. For instance, your image hosting may live elsewhere on the internet and blog's dependence on an image service.

Unique request processing invokes advanced development skills not covered by blogging tools, but Django can propel this task. 

Please consult your site owner about the possibility.

With infinite storage, there is a "limitless barrier" to how many sites you can create. However, your branding is connected to a single entry. In other words, from a list of sites you can only select one to serve as the namesake. More importantly, whatever Site is holding ID `1`, typically the first entry, is the one providing all the appearance for your website. For more details look to [the Site Framework docmentation](https://docs.djangoproject.com/en/dev/ref/contrib/sites/).
`

## Find the default site

As previously mentioned, the Site associated with `ID 1` is the authority of your website branding. The display list can tell you at a glance what the IDs are. 

For quick results - on a testing server, navigate to [http://127.0.0.1:8000/admin/sites/site/1/](http://127.0.0.1:8000/admin/sites/site/1/). In production, replace the IP address `127.0.0.1' with your own address with the appended paths. You may need to authenticate first.

You will either be relocated to data inside editor mode, or if the object does not exist, then a warning will appear onscreen.
