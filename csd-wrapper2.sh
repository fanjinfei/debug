> run_curl --data-ascii @-

> "https://$CSD_HOSTNAME/+CSCOE+/sdesktop/scan.xml?reusebrowser=1" 

> <<-END endpoint.policy.location="Default";

> endpoint.enforce="success";

> endpoint.fw["MSWindowsFW"]={};

> endpoint.fw["MSWindowsFW"].exists="true";

> endpoint.fw["MSWindowsFW"].enabled="ok";

> endpoint.as["MicrosoftAS"]={};

> endpoint.as["MicrosoftAS"].exists="true";

> endpoint.as["MicrosoftAS"].activescan="ok";

> endpoint.av["MicrosoftAV"]={};

> endpoint.av["MicrosoftAV"].exists="true";

> endpoint.av["MicrosoftAV"].activescan="ok";

> END
