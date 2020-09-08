//var cliOutput;
var respOutput = "";
var enableConsoleLoggingWrkr = false;
var isEmptyBlockCLIWorker = false;

function consoleLogWrkr(consoleString)
{
  if (enableConsoleLoggingWrkr) {
    console.log(consoleString + "\n");
  }
}

function consoleLogMethodDetailsWrkrEnd(className, methodName) {
  if (enableConsoleLoggingWrkr) {
    //consoleLogMethodDetailsWrkr(className, methodName, "end");
  }
}

function consoleLogMethodDetailsWrkrStart(className, methodName) {
  if (enableConsoleLoggingWrkr) {
    //consoleLogMethodDetailsWrkr(className, methodName, "start");
  }
}

function consoleLogMethodDetailsWrkr(className, methodName, startOrEnd) {
  if (enableConsoleLoggingWrkr) {
    var stringToPrint = className + " - " + methodName + " - " + startOrEnd;
    console.log(stringToPrint + "\n")
    if (startOrEnd != null && startOrEnd != undefined && startOrEnd === 'start') {
      console.time("Time taken for Function " + methodName);
    } else if (startOrEnd != null && startOrEnd != undefined && startOrEnd === 'end') {
      console.timeEnd("Time taken for Function " + methodName);
    }
  }
}


function getCmdOutputHandled(cliName, clis, isExec, messagePost) {
  //consoleLogMethodDetailsWrkrStart("cliWorker.js", "getCmdOutputHandled()");
  try {
    getCmdOutput(cliName, clis, isExec, messagePost);
  }
  catch (e) {
    ////consoleLogWrkr(e.errorResponse);
    respOutput = "";
  }
  //consoleLogMethodDetailsWrkrEnd("cliWorker.js", "getCmdOutputHandled()");
  return respOutput;
}
function getCmdOutputsHandled(cliNames,cliNamesAndCliObj, messagePost) {
  //consoleLogMethodDetailsWrkrStart("cliWorker.js", "getCmdOutputHandled()");
  try {
      var outPutCliNameAndOutPut={};
      for(var name in cliNamesAndCliObj){
          //var cliName=name;
            if (cliNamesAndCliObj.hasOwnProperty(name)) {
          var cli=cliNamesAndCliObj[name];
           var outPut=getCmdOutput(cliNames, cli, true, false);
           outPutCliNameAndOutPut[name]=outPut;
            }
      }
      if(messagePost){
           var cliJson = [
            {"cliName": cliNames, "outputObj": outPutCliNameAndOutPut}
          ];
          postMessage(JSON.stringify(cliJson));

      }else{
      return outPutCliNameAndOutPut;
      }

  }
  catch (e) {
    ////consoleLogWrkr(e.errorResponse);
    respOutput = "";
  }
  //consoleLogMethodDetailsWrkrEnd("cliWorker.js", "getCmdOutputHandled()");
  return respOutput;
}
//setInterval(function(){//consoleLogWrkr('hiii');},3000);
var CMD_HTTP_URL = '/ios_web_exec/commandset',
  INFO_MESSAGES = ["#exit",
    "# exit",
    "Note: Issue",
    "Not all config may be removed",
    "3G Modem is not inserted",
    "Cannot send CHV1 to modem for verification. It will be sent when the SIM becomes active.",
    "Building configuration",
    "Not all config may be removed and may reappear after",
    "set to default configuration",
    "Translating",
    "WAN interface will be disabled",
    "DSL interfaces will be disabled",
    "Cannot enable CDP on this interface",
    "Changing media to",
    "Mode no change",
    "Default route without gateway",
    "Dynamic mapping not found",
    "Unknown physical layer",
    "Warning:",
    "Policy already has same proposal set",
    "IKEv2 Profile default not found",
    "Start IPS global disable"];
function getCmdOutput(cliName, clis, isExec, messagePost) {
  if (!clis) {
    return;
  }

  var xhr;
  //var cliOutput = "";

  if (typeof XMLHttpRequest !== 'undefined'){
    xhr = new XMLHttpRequest();
  }
  else {
    var versions = ["MSXML2.XmlHttp.5.0",
      "MSXML2.XmlHttp.4.0",
      "MSXML2.XmlHttp.3.0",
      "MSXML2.XmlHttp.2.0",
      "Microsoft.XmlHttp"];

    for (var i = 0, len = versions.length; i < len; i++) {
      try {
        xhr = new ActiveXObject(versions[i]);
        break;
      }
      catch (e) {
                    isEmptyBlockCLIWorker = true;
      }
    }
  }

  xhr.onreadystatechange = ensureReadiness;

  function ensureReadiness() {
    if (xhr.readyState < 4) {
      return;
    }

    if (xhr.status !== 200) {
      return;
    }

    // all is well
    if (xhr.readyState === 4) {
      //callback(xhr);
      try {
        var cliOutput;
        cliOutput = getCLI(xhr.responseText, clis, isExec);
        ////consoleLogWrkr(cliOutput);
        if (messagePost) {
          var cliJson = [
            {"cliName": cliName, "output": cliOutput}
          ];
          postMessage(JSON.stringify(cliJson));
        } else {
          respOutput = cliOutput;
        }

      }
      catch (e) {
        ////consoleLogWrkr(e.errorResponse);
        if (messagePost) {
          var cliJson = [
            {"cliName": cliName, "output": ""}
          ];
          postMessage(JSON.stringify(cliJson));
        }else{
            respOutput = "";
        }
      }
    }
  }
  xhr.open('POST', CMD_HTTP_URL, false);
  xhr.send(addHeaderAndFooter(clis, isExec));
  if(!messagePost){
      return respOutput;
  }

}
function getCLI(data, clis, isExec) {
  //consoleLogMethodDetailsWrkrStart("cliWorker.js", "getCLI()");

  ////consoleLogWrkr(data);
  var retResponse = "",
    throwError = {
      errorCmd: "",
      errorResponse: ""
    };
  if (data.indexOf("! COMMANDSET") === -1) {
    throwError.errorCmd = clis;
    throwError.errorResponse = data;
    throw throwError;
  }
  if (data.indexOf("STATUS=\"0\"") === -1) {
    throwError.errorCmd = clis;
    throwError.errorResponse = data;
    throw throwError;
  }

  var cmd = "",
    response = "",
    cmdBeginIndex = data.indexOf("! COMMAND BEGIN"),
    cmdEndIndex = data.indexOf("! COMMAND END"),
    respBeginIndex = data.indexOf("! OUTPUT BEGIN"),
    respEndIndex = data.indexOf("! OUTPUT END"),
    parseErrorIndex = data.indexOf("PARSE_ERROR"),
    error = data.substring(parseErrorIndex + 13, parseErrorIndex + 14);
  ////consoleLogWrkr(error);

  while (respBeginIndex !== -1) {
    cmd = data.substring(cmdBeginIndex + 16, cmdEndIndex);
    response = response + data.substring(respBeginIndex + 15, respEndIndex);
    ////consoleLogWrkr(response);
    cmd = cmd.trim();
    response = response.trim();
    if (error != 0) {
      throwError.errorCmd = cmd;
      if (error == 2 && response == "") {
        throwError.errorResponse = "Invalid input detected.";
      } else {
        throwError.errorResponse = response;
      }
      throw throwError;
    }
    if ((response.indexOf("Invalid input") !== -1) || (response.indexOf("Unrecognized command") !== -1)) {
      throwError.errorCmd = cmd;
      throwError.errorResponse = response;
      throw throwError;
    }

    if ((error == 0) && (!isExec)) {
      if (!isInfoMessage(response)) {
        response = $.trim(response);
        if (response !== "") {
          throwError.errorCmd = cmd;
          throwError.errorResponse = response;
          throw throwError;
        }
      } else {
        response = "";
      }
    }

    cmdBeginIndex = data.indexOf("! COMMAND BEGIN", cmdBeginIndex + 1);
    cmdEndIndex = data.indexOf("! COMMAND END", cmdEndIndex + 1);
    respBeginIndex = data.indexOf("! OUTPUT BEGIN", respEndIndex + 1);
    respEndIndex = data.indexOf("! OUTPUT END", respBeginIndex + 1);
    parseErrorIndex = data.indexOf("PARSE_ERROR", parseErrorIndex + 1);
      error = data.substring(parseErrorIndex + 13, parseErrorIndex + 14);
  }

  retResponse = response;
  //consoleLogMethodDetailsWrkrEnd("cliWorker.js", "getCLI()");

  return retResponse;
}
function isInfoMessage(resp) {
  //consoleLogMethodDetailsWrkrStart("cliWorker.js", "isInfoMessage()");

  var found = false,
    i = INFO_MESSAGES.length;
  for (i = (INFO_MESSAGES.length - 1); i >= 0; i = (i - 1)) {
    if (resp.indexOf(INFO_MESSAGES[i]) !== -1) {
      found = true;
      break;
    }
  }
  //consoleLogMethodDetailsWrkrEnd("cliWorker.js", "isInfoMessage()");
  return found;
}
function addHeaderAndFooter(clis, isExec) {
  return "! COMMANDSET VERSION=\"1.0\"\n" +
    "! OPTIONS BEGIN\n! MODE=\"" + (isExec ? "0" : "1") + "\"\n" +
    "! OPTIONS END\n" +
    clis + "\n" +
    "! END\n! COMMANDSET END";
}
