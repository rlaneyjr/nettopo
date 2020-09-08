importScripts("cliWorker.js");
var runCliInterval, featureState;
onmessage = function(e) {
  jsonObject = JSON.parse(e.data);
  if (jsonObject[0]["type"] == "start") {
    featureState = jsonObject;
    getOneTimeSecurityData(jsonObject[0]["type"]);
    getSecurityData(jsonObject[0]["type"]);
  }

  if (runCliInterval != undefined) {
    clearInterval(runCliInterval);
  }
  var timeInterval = jsonObject[0]["poll"];
  runCliInterval = setInterval(function() {
    getSecurityData(jsonObject[0]["type"]);

  }
  , timeInterval);
};

//function getCmdOutputHandledForSecurityDashboard(cliName,clis, isExec,messagePost){
//
//  try{
//    //consoleLogWrkr("in SecurityDashboardWorker command - "+clis);
//
//    var commandOutput = getCommandInLocalStorage(clis);
//    //consoleLogWrkr("in SecurityDashboardWorker got CACHE command ojbect " + commandOutput);
//
//
//    var execCmdOutput;
//    if (commandOutput == null || commandOutput == undefined) {
//          //consoleLogWrkr("In SecurityDashboardWorker Command NOT FOUND IN CACHE. Executing - "+clis);
//          execCmdOutput = getCmdOutputHandled(cliName,clis, isExec,messagePost);
//    } else if ((commandOutput != null && commandOutput != undefined) && (!commandOutput["Latest"] || !commandOutput["DataLoadSuccess"])) {
//          //If the command is latest, it will be fetched and sent back.
//          //If not, it will be loaded and that data is returned.
//          //consoleLogWrkr("In SecurityDashboardWorker Command found. BUT NOT LATEST. Executing - "+clis);
//          execCmdOutput = getCmdOutputHandled(cliName,clis, isExec,messagePost);
//          commandOutput["CLIOutput"] = execCmdOutput;
//          commandOutput["Reloads"] = commandOutput["Reloads"]+1;
//          commandOutput["ReloadInProgress"] = false;
//          commandOutput["DataLoadSuccess"] = true;
//          commandOutput["Latest"] = true;
//    }
//    else if (commandOutput != null && commandOutput != undefined && commandOutput["Latest"] && commandOutput["DataLoadSuccess"]) {
//          //consoleLogWrkr("In SecurityDashboardWorker Command found. LATEST IN CACHE. Getting data for - "+clis);
//          commandOutput["Reads"] = commandOutput["Reads"]+1;
//          execCmdOutput = commandOutput["CLIOutput"];
//          //Below method prints the current read/write/status of the cache entry. CLI output is not printed.
//          getCacheCLIAccessDetails(commandOutput);
//    }
//
//    respOutput = execCmdOutput;
//    //consoleLogWrkr("in CLIWORKER command output - "+commandOutput);
//
//  }
//  catch(e) {
//            ////consoleLogWrkr(e.errorResponse);
//      respOutput="";
//        }
//  return respOutput;
//}

function getOneTimeSecurityData(type) {
  //consoleLogMethodDetailsWrkrStart("securityDashboardWorker.js", "getOneTimeSecurityData()");
  if (featureState[0]["ips"]) {
    getCmdOutputHandled("ipsStats", "show ip ips signatures detail | section include Y( +)Y", true, true);
    ipsAttackResp = getCmdOutputHandled("ipsAttack", "show logging | i %IPS", true, true);
  } else {
    if (type == "start") {
      emptyPost("ipsStats");
      emptyPost("ipsAttack");
    }
  }
  //consoleLogMethodDetailsWrkrEnd("securityDashboardWorker.js", "getOneTimeSecurityData()");
}

//to remove loader if feature not enabled
function emptyPost(cliName) {
  //consoleLogMethodDetailsWrkrStart("securityDashboardWorker.js", "emptyPost()");
  var cliJson = [
    {"cliName": cliName, "output": ""}
  ];
  postMessage(JSON.stringify(cliJson));
  //consoleLogMethodDetailsWrkrEnd("securityDashboardWorker.js", "emptyPost()");
}

function getSecurityData(type) {
  //consoleLogMethodDetailsWrkrStart("securityDashboardWorker.js", "getSecurityData()");
  var cliJson;
  getCmdOutputHandled("topAppsBit", "show ip nbar protocol-discovery stats bit-rate", true, true);
  getCmdOutputHandled("ipcache", "show ip admission cache", true, true);
  getCmdOutputHandled("topUsers", "show flow monitor application-mon cache aggregate ipv4 source address", true, true);
  getCmdOutputHandled("topAppsByte", "show ip nbar protocol-discovery stats byte-count top-n 10", true, true);

  //cws (if enabled then send http request)
  if (featureState[0]["cws"]){
    getCmdOutputHandled("cws", "show cws statistics", true, true);
  }
  else {
    if (type == "start"){
      emptyPost("cws");
    }
  }

  //ips (if enabled then send http request)
  if (featureState[0]["ips"]) {
    getCmdOutputHandled("ips", "show ip ips statistics", true, true);
  } else {
    if (type == "start"){
      emptyPost("ips");
    }
  }

  //vpn (if enabled then send http request)
  if (featureState[0]["vpn"]) {
    tunnel0 = getCmdOutputHandled("tunnel", "show interfaces Tunnel0", true, false);
    tunnel1 = getCmdOutputHandled("tunnel", "show interfaces Tunnel1", true, false);
    cliJson = [
      {"cliName": "tunnel", "output1": tunnel0, "output2": tunnel1}
    ];
    postMessage(JSON.stringify(cliJson));
    getCmdOutputHandled("vpn", "show crypto session detail", true, true);
  } else {
    if (type == "start") {
      emptyPost("vpn");
      cliJson = [
        {"cliName": "tunnel", "output1": "", "output2": ""}
      ];
      postMessage(JSON.stringify(cliJson));
    }
  }

  cliJson = [
    {"cliName": "loadTile"}
  ];
  postMessage(JSON.stringify(cliJson));

  //policy (if enabled then send http request)
  if (featureState[0]["policy"]){
    getCmdOutputHandled("policy", "show policy-map type inspect zone-pair", true, true);
  }
  else {
    if (type == "start"){
      emptyPost("policy");
    }
  }


  getCmdOutputHandled("firewallDrop", "show policy-firewall stats drop-counters", true, true);
  var int1 = "", int2 = "";
  if (featureState[0]['int1'].trim() != ""){
    int1 = getCmdOutputHandled("wanInt", "show interfaces " + featureState[0]['int1'], true, false);
  }
  if (featureState[0]['int2'].trim() != ""){
    int2 = getCmdOutputHandled("wanInt", "show interfaces " + featureState[0]['int2'], true, false);
  }
  cliJson = [
    {"cliName": "wanInt", "int1": int1, "int2": int2}
  ];
  postMessage(JSON.stringify(cliJson));
  //consoleLogMethodDetailsWrkrEnd("securityDashboardWorker.js", "getSecurityData()");

}