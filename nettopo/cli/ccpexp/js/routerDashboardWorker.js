importScripts("cliWorker.js");
onmessage = function(e) {
  var msg = JSON.parse(e.data);
  if (msg[0]['type'] == "start"){
    getRouterDashboardDataFirstTime(msg);
  }
  else{
    getRouterDashboardData(msg);
  }
};

//function getCmdOutputHandledForDashboard(cliName,clis, isExec,messagePost){
//
//  try{
//    //consoleLogWrkr("in RouterDashboardWorker command - "+clis);
//
//    var commandOutput = getCommandInLocalStorage(clis);
//    //consoleLogWrkr("in RouterDashboardWorker got CACHE command ojbect " + commandOutput);
//
//
//    var execCmdOutput;
//    if (commandOutput == null || commandOutput == undefined) {
//          //consoleLogWrkr("In RouterDashboardWorker Command NOT FOUND IN CACHE. Executing - "+clis);
//          execCmdOutput = getCmdOutputHandled(cliName,clis, isExec,messagePost);
//    } else if ((commandOutput != null && commandOutput != undefined) && (!commandOutput["Latest"] || !commandOutput["DataLoadSuccess"])) {
//          //If the command is latest, it will be fetched and sent back.
//          //If not, it will be loaded and that data is returned.
//          //consoleLogWrkr("In RouterDashboardWorker Command found. BUT NOT LATEST. Executing - "+clis);
//          execCmdOutput = getCmdOutputHandled(cliName,clis, isExec,messagePost);
//          commandOutput["CLIOutput"] = execCmdOutput;
//          commandOutput["Reloads"] = commandOutput["Reloads"]+1;
//          commandOutput["ReloadInProgress"] = false;
//          commandOutput["DataLoadSuccess"] = true;
//          commandOutput["Latest"] = true;
//    }
//    else if (commandOutput != null && commandOutput != undefined && commandOutput["Latest"] && commandOutput["DataLoadSuccess"]) {
//          //consoleLogWrkr("In RouterDashboardWorker Command found. LATEST IN CACHE. Getting data for - "+clis);
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

function getRouterDashboardData(msg) {
  //consoleLogMethodDetailsWrkrStart("routerDashboardWorker.js", "getRouterDashboardData()");

  var cliJson, int1 = "", int2 = "";
  getCmdOutputHandled("environment", "show environment all", true, true);
  getCmdOutputHandled("shRun", "show running-config | format", true, true);
  getCmdOutputHandled("cpuUtil", "show processes cpu | format " + msg[0]['installDir'] + "/odm/overviewshCpuUtil.odm", true, true);
  if (msg[0]['int1'].trim() != ""){
    int1 = getCmdOutputHandled("wanInt", "show interfaces " + msg[0]['int1'], true, false);
  }
  if (msg[0]['int2'].trim() != ""){
    int2 = getCmdOutputHandled("wanInt", "show interfaces " + msg[0]['int2'], true, false);
  }
  cliJson = [
    {"cliName": "wanInt", "int1": int1, "int2": int2}
  ];
  postMessage(JSON.stringify(cliJson));
  getCmdOutputHandled("flashMem", "show file systems | format " + msg[0]['installDir'] + "/odm/overviewshFileSystem.odm", true, true);
  getCmdOutputHandled("systemMem", "show processes memory | format " + msg[0]['installDir'] + "/odm/overviewshProcMemory.odm", true, true);
  getCmdOutputHandled("shversion", "show version", true, true);
  getCmdOutputHandled("interface", "show ip interface brief | format", true, true);
  cliJson = [
    {"cliName": "stop"}
  ];
  postMessage(JSON.stringify(cliJson));

  //consoleLogMethodDetailsWrkrEnd("routerDashboardWorker.js", "getRouterDashboardData()");

}
function getRouterDashboardDataFirstTime(msg) {
  //consoleLogMethodDetailsWrkrStart("routerDashboardWorker.js", "getRouterDashboardDataFirstTime()");

  //getCmdOutputHandled("shversion","show version",true,true);
  //getCmdOutputHandled("clock","show clock",true,true);

  var cliJson, int1 = "", int2 = "";
  getCmdOutputHandled("environment", "show environment all", true, true);
  getCmdOutputHandled("interface", "show ip interface brief | format", true, true);
  //getCmdOutputHandled("shrunformat","show run | format",true,true);
  getCmdOutputHandled("cpuUtil", "show processes cpu | format " + msg[0]['installDir'] + "/odm/overviewshCpuUtil.odm", true, true);
  if (msg[0]['int1'].trim() != ""){
    int1 = getCmdOutputHandled("wanInt", "show interfaces " + msg[0]['int1'], true, false);
  }
  if (msg[0]['int2'].trim() != ""){
    int2 = getCmdOutputHandled("wanInt", "show interfaces " + msg[0]['int2'], true, false);
  }
  cliJson = [
    {"cliName": "wanInt", "int1": int1, "int2": int2}
  ];
  postMessage(JSON.stringify(cliJson));
  getCmdOutputHandled("flashMem", "show file systems | format " + msg[0]['installDir'] + "/odm/overviewshFileSystem.odm", true, true);
  getCmdOutputHandled("systemMem", "show processes memory | format " + msg[0]['installDir'] + "/odm/overviewshProcMemory.odm", true, true);
  //shRun=getCmdOutputHandled("deviceDetails","show run | format",true,false);

  shVerFormat = getCmdOutputHandled("shVerFormat", "show version | format " + msg[0]['installDir'] + "/odm/overviewshVer.odm", true, false);
  shVer = getCmdOutputHandled("shversion", "show version", true, false);
  cliJson = [
    {"cliName": "deviceDetailsFirst", "shVerFormat": shVerFormat, "shVer": shVer}
  ];
  postMessage(JSON.stringify(cliJson));
  cliJson = [
    {"cliName": "stop"}
  ];
  postMessage(JSON.stringify(cliJson));
  //consoleLogMethodDetailsWrkrEnd("routerDashboardWorker.js", "getRouterDashboardDataFirstTime()");

}
