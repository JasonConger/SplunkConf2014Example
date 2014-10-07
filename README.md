Splunk .conf 2014 Example Application
===

This is an example app from my Splunk .conf 2014 session titled "Notes From the Field: Splunk Application Building and Automation".  The goal of this application is to demonstrate the following:

* App build automation with Apache Ant.
    - Build automation creates a clean app environment on every build to ensure your experience will be what the end user will experience on initial installation.
    - Build automation ensures [packaging guidelines](http://docs.splunk.com/Documentation/Splunk/latest/AdvancedDev/PackageApp) are followed and reduces human error.
* Automatically copying a TA to $SPLUNK_HOME/etc/apps on first run.
* Application setup methods.  For example, prompting users for inupt on the initial run of an application.
