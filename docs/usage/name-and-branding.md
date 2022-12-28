# Name and branding 

Your website branding such as page titles and copyright signage, all appear with a placeholder - `example.com`. 

These options are customisable from the admin panel, under the banner of our Sites module. 

Site modules direct link [http://127.0.0.1:8000/admin/sites/site/](http://127.0.0.1:8000/admin/sites/site/).

## Customise your site title
1. Open the admin portal
2. Click through to **Sites** > **example.com**
3. Specify your site in the fields 
4. Finish by **Save**

The required fields mean the following:

**Domain name**

The fully qualified domain name associated with the website. For example, www.example.com.

**Display name**

A human-readable “verbose” name for the website.

## Deleting example.com entry

Yes, you are free to delete the example object. Beware of the fact that if you have not already updated the default settings then names will disappear.

You can identify a problem when **"No Title"** error appears on your pages. This error means a Site object does not exist or the SITE_ID is missing.

If you are experiencing a disruption after deleting the example name, you have some options to reverse the error.

Start by accessing the admin portal:
1. Open the admin portal
2. Click **Sites**
3. Proceed with **Add Site +**
4. Enter valid display and domain names
5. Save

Use the ID value, it will be assigned upon saving. SITE_ID lives in the `settings.py` file and the original value is **1**. Amend the configuration to reflect whichever ID you have chosen. A server restart is likely after this change.

Then you should visit your homepage to review the changes and check functionality has returned to normal, with your domain appearing in the title.

## Managing multiple sites 

When posts are contextual in nature, then the blog relies on the Site module to inform traffic. A single content store can be used on different domains. For example, `DjangoNews.com` publishes content and `GamingDjango.com` uses its content to feature gaming news.

### Brief history of Sites
Django was originally developed at a newspaper to publish content on multiple domains; using one single content base. There was a desire from the newspaper's staff to associate articles with multiple sites and avoiding duplication. 

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
