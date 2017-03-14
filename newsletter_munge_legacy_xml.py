#!/usr/bin/env python
# -*- coding: utf-8 -*-
from lxml import objectify

import datetime
import os
import platform
import pprint
import sys
import urllib2
from StringIO import StringIO

from legacy_settings import LEGACY_PW, OUTFILE_PATH

'''
This script outputs two files based on requesting and parsing a Legacy XML file:
'obitsLegacy.html'
'obitsLegacyLinksByDate.html'

If you pass an integer, you'll get a version of the date-based
list that many days long. e.g., "./get_legacies_xml.py 5" will output 5 days'
worth into files named:
'obitsLegacyCustom.html'
'obitsLegacyLinksByDateCustom.html'

Otherwise, with no extra argument, the default is 30 days into the files as
above.

================================================================================

Each obit XML tree looks like this:

<Notice>
  <PersonId>172048590</PersonId>
  <NamePrefix></NamePrefix>
  <NameAdditionalPrefix></NameAdditionalPrefix>
  <FirstName>Chandler</FirstName>
  <MiddleName>Harrison</MiddleName>
  <LastName>Barkelew</LastName>
  <NameSuffix></NameSuffix>
  <NameAdditionalSuffix></NameAdditionalSuffix>
  <MaidenName></MaidenName>
  <City>Eugene</City>
  <State>OR</State>
  <Country>United States</Country>
  <DateEntered>2014-08-10T00:00:00</DateEntered>
  <DateCompleted>2014-08-10T00:00:00</DateCompleted>
  <DateExpired>2014-09-09T00:00:00</DateExpired>
  <NoticeText>&lt;!-- Fullname = Chandler Harrison Barkelew --&gt;&lt;IMG SRC="/Images/Cobrands/RegisterGuard/Photos/BARKELEW_CHANDLER_14_CC_08102014.jpg" ALIGN="LEFT" vspace="4" hspace="10" lgyOrigName="BARKELEW_CHANDLER_14_CC.jpeg"&gt;October 12, 1919 -&lt;br/&gt;July 31, 2014&lt;br&gt;&lt;br&gt;Chandler was born in Fresno, California to Vern Barkelew and Helen (Harrison) Barkelew. He passed away at the age of 94. He is survived by his wife of 67 years Virginia (Koorn); his children Claire Barkelew Depenbrock, James Barkelew and Julia Smith; his four grandchildren Chandler and Sarah Depenbrock and Jonathan and Tyler Barkelew; and his brother, Verne Spencer Barkelew. &lt;br&gt;&lt;br&gt;Chandler graduated from Alhambra High School and Pomona College, Phi Beta Kappa, then earned a PhD in chemistry at the University of California at Berkeley. He was involved in the Manhattan Project and early research of nuclear energy. &lt;br&gt;&lt;br&gt;He worked as a research chemist for Shell Oil for 39 years in Emeryville, California; the Hague Netherlands; Oakridge, Tennessee and Houston, Texas. He was well respected in the field of chemical engineering and authored numerous technical publications. He was a member of American Chemical Society, American Institute of Chemical Engineers, Sigma Xi and Chemical Heritage Society.&lt;br&gt;&lt;br&gt;Chandler and Virginia loved to travel. They enjoyed many trips to Europe, Canada and around the United States. He was a talented clarinetist with a lifelong love of classical music.&lt;br&gt;&lt;br&gt;Chandler was a man of great intelligence, quiet dignity and a wonderful sense of humor.&lt;br&gt;&lt;br&gt;At his request no services will be held. Arrangements by Virgil T. Golden Funeral Service. In lieu of flowers, please make a donation to your favorite academic scholarship fund.&lt;br&gt;&lt;br&gt;</NoticeText>
  <NoticeType>Paid</NoticeType>
  <Status>Active</Status>
  <FromToYears>1919-2014</FromToYears>
  <AffiliateSite>RegisterGuard</AffiliateSite>
  <AffiliateAdId>6043905</AffiliateAdId>
  <PublishedBy>Eugene Register-Guard</PublishedBy>
  <DisplayURL>http://www.legacy.com/Link.asp?I=LS000172048590</DisplayURL>
  <LocationList>Eugene</LocationList>
  <FHIndex>7982</FHIndex>
  <FHName>Virgil T. Golden Funeral Service and Oakleaf Crematory</FHName>
  <FHKnownByName1>Virgil T. Golden Funeral Service and Oakleaf Crematory</FHKnownByName1>
  <FHAddressLine1>605 Commercial St SE</FHAddressLine1>
  <FHCity>Salem</FHCity>
  <FHStateProvince>OR</FHStateProvince>
  <FHZipCode>97301</FHZipCode>
  <FHPhoneNumber1>(503) 364.2257</FHPhoneNumber1>
  <FHUrl>www.vtgolden.com</FHUrl>
  <ShowInSpotlight>0</ShowInSpotlight>
  <DateCreated>2014-08-09T23:13:11.670</DateCreated>
  <ImageUrl>http://mi-cache.legacy.com/legacy/images/Cobrands/RegisterGuard/Photos/BARKELEW_CHANDLER_14_CC_08102014.jpg</ImageUrl>
  <RowVersion>769416943</RowVersion>
  <GuestBookURL>http://www.legacy.com/Link.asp?I=GB000172048590</GuestBookURL>
</Notice>
'''

DAYS_BACK = 30
TODAY = datetime.date.today()
OUTFILE_DATE = 'obitsLegacyLinksByDate.html'
OUTFILE_DATE_CUSTOM = 'obitsLegacyLinksByDateCustom.html'
OUTFILE_ALPHA = 'obitsLegacy.html'
OUTFILE_ALPHA_CUSTOM = 'obitsLegacyCustom.html'

if platform.platform().count('Linux'): # running on AWS EC2 instance, probably ...
    OUTFILE_PATH = OUTFILE_PATH
else: # testing locally, probably ...
    OUTFILE_PATH = os.path.realpath(os.path.join(os.path.dirname(__file__)))

def main(DAYS_BACK=None, custom=None):
    # Loop through number of DAYS_BACK ...
    main_string = ''
    outstring = ''
    alpha_list = []
    alpha_list_out = []
    for i in xrange(DAYS_BACK):
        # Get the date for the day's XML feed URL ...
        i_days_ago = TODAY - datetime.timedelta(days=i)
        i_days_ago_string = i_days_ago.strftime('%Y%m%d')

        # Parse the day's XML feed ...
        # https://www.legacy.com/services/notices.asp?Affiliate=registerguard&Password=LEGACY_PW&RunDate=20140101
        raw_doc = urllib2.urlopen(
            'https://www.legacy.com/services/notices.asp?Affiliate=registerguard&Password=%s&RunDate=%s' % (LEGACY_PW, i_days_ago_string)).read()
        doc = objectify.parse(StringIO(raw_doc))
        tree = doc.getroot()

        # Munging strings used in the final product/output ...
        legacy_site_date_page_url = 'http://www.legacy.com/obituaries/registerguard/obituary-search.aspx?daterange=0&specificdate=%s&countryid=1&stateid=48&affiliateid=1765&entriesperpage=50' % (
            i_days_ago.strftime("%Y%m%d"))
        pre_string = u'\t<a href="%s" target="_blank"><h1>%s</h1></a>\n\t<div class="obituary_date">\n' % (
            legacy_site_date_page_url, i_days_ago.strftime('%A, %B %-d, %Y'))

        days_obits = tree[
            '{urn:schemas-microsoft-com:xml-sql}query'].getchildren()
        if days_obits:
            print 'Obits today! %s' % i_days_ago_string
            for e in days_obits:
                if e.MaidenName:
                    maiden_name = u'(%s)' % e.MaidenName
                else:
                    maiden_name = ''
                main_string += u'\t\t<a href="%s" target="_blank"><h2>%s %s %s %s %s %s %s %s</h2></a>\n' % \
                    (
                        e.DisplayURL,
                        e.NamePrefix,
                        e.NameAdditionalPrefix,
                        e.FirstName,
                        e.MiddleName,
                        maiden_name,
                        e.LastName,
                        e.NameSuffix,
                        e.NameAdditionalSuffix,
                    )

                image_url = getattr(e, 'ImageUrl', '')
                if image_url:
                    main_string += u'\t\t<a href="{0}" target="_blank"><img src="{1}" alt="{2} {3}" /></a>\n'.format(
                        e.DisplayURL,
                        image_url,
                        e.FirstName,
                        e.LastName,
                    )

                # Clean up date for alpha_list ...
                date_obj = datetime.datetime.strptime(e.DateCompleted.text, '%Y-%m-%dT00:00:00')
                formatted_date_str = date_obj.strftime('%B %d, %Y')
                # Gather names here for alpha_list ...
                alpha_list.append([ e.LastName, e.FirstName, formatted_date_str, e.DisplayURL ])
                
                # try:
                #     print '   ', e.ImageUrl.text
                # except AttributeError, err:
                #     print err
        else:
            print 'Aw man, no Obits today! %s' % i_days_ago_string
            main_string = u'<li>No obituaries published.</li>\n'

        daily_string = pre_string + main_string + u'\t</div> <!-- /.obituary_date -->\n'
        outstring += daily_string
        # Clean out main_string for next loop/day's use ...
        main_string = u''

    if custom:
        outfile = open(os.path.join(OUTFILE_PATH, OUTFILE_DATE_CUSTOM), 'w')
    else:
        outfile = open(os.path.join(OUTFILE_PATH, OUTFILE_DATE), 'w')

    outstring = '<div class="obituaries_by_date">\n{0}\n</div> <!-- /.obituaries_by_date -->'.format(outstring.rstrip())
    outfile.write(outstring.encode('utf-8'))
    outfile.close()

    '''
    alpha_list_item:
    ['Zaninovich',
    'Martin',
    'July 19, 2014',
    'http://www.legacy.com/Link.asp?I=LS000171779531'],
    '''
    alpha_list.sort()
    for alpha_list_item in alpha_list:
        alpha_list_out.append('<li><a href="%s">%s, %s</a><br><small style="text-transform:uppercase; color: #666; letter-spacing:.05em; font-family:arial,san-serif;">%s</small></li>' % (alpha_list_item[3], alpha_list_item[0], alpha_list_item[1], alpha_list_item[2]))
    alpha_string_out = '<ul class="li2">\n' + '\n'.join(alpha_list_out) + '</ul>\n'
    
    if custom:
        outfile_alpha = open(os.path.join(OUTFILE_PATH, OUTFILE_ALPHA_CUSTOM), 'w')
    else:
        outfile_alpha = open(os.path.join(OUTFILE_PATH, OUTFILE_ALPHA), 'w')
    outfile_alpha.write(alpha_string_out.encode('utf-8'))
    outfile_alpha.close()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        custom = True
        main(DAYS_BACK=int(sys.argv[1]), custom=True)
    else:
        main(30, custom = False)
