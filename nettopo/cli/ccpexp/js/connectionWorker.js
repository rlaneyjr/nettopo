importScripts("cliWorker.js");
onmessage = function(e) {
  jsonObject = JSON.parse(e.data);
  if (jsonObject[0]["name"] == "shinterface") {
    getCmdOutputHandled("shInterace", "show interfaces " + jsonObject[0]["data"], true, true);
  } else if (jsonObject[0]["name"] == "shdns") {
    getCmdOutputHandled("shIpDns", "show ip dns view", true, true);
  } else if (jsonObject[0]["name"] == "ping") {
    getCmdOutputHandled("ping", "ping www.cisco.com source " + jsonObject[0]["data"], true, true);
  } else if (jsonObject[0]["name"] == "pingDomain") {
    testInternetConnection();
  }
};

function testInternetConnection() {
  //consoleLogMethodDetailsWrkrStart("connectionWorker.js", "testInternetConnection()");

  var flag = "false";
  var xhr = new XMLHttpRequest();
  var file = "http://www.cisco.com";
  var randomNum = Math.round(Math.random() * 10000);
  xhr.open('HEAD', file + "?rand=" + randomNum, false);
  try {
    xhr.send();
    if (xhr.status >= 200 && xhr.status < 304) {
      flag = "true";
    } else {
      flag = "false";
    }
  } catch (e) {
    flag = "false";
  }
  var cliJson = [
    {"cliName": "pingDomain", "output": flag}
  ];
  postMessage(JSON.stringify(cliJson));
  //consoleLogMethodDetailsWrkrEnd("connectionWorker.js", "testInternetConnection()");
}