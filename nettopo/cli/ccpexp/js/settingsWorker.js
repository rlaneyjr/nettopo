importScripts("cliWorker.js");
onmessage = function(e) {
  jsonObject = JSON.parse(e.data);
  if (jsonObject[0]["name"] == "upgradeCCP") {
    startUpgrade(jsonObject[0]["dir"],jsonObject[0]["file"],jsonObject[0]["deleteTar"],jsonObject[0]["fileSize"]);
  } else if (jsonObject[0]["name"] == "preferences") {
        savePreferences(jsonObject[0]["fileLoc"],jsonObject[0]["json"]);
  }else if (jsonObject[0]["name"] == "reset") {
    resetRouter(jsonObject[0]["file"]);
  }
  else if (jsonObject[0]["name"] == "upgradeIOS") {
    startIosUpgrade(jsonObject[0]["dir"],jsonObject[0]["file"],jsonObject[0]["fileSize"]);
  }
  else if (jsonObject[0]["name"] == "upgradeIosViaDialog") {
    startIosUpgradeViaDialog(jsonObject[0]["dir"],jsonObject[0]["file"],jsonObject[0]["deleteBootList"]);
  }
};

function resetRouter(fileLoc){
    getCmdOutputHandled("writeMemory", "write memory", true, false);
    var copyConfig="copy "+fileLoc+" startup-config";
    getCmdOutputHandled("copyConfig", copyConfig, true, true);
    getCmdOutputHandled("reload", "reload", true, true);
    var testFlag=testDeviceConnection();
    while(!testFlag){
  testFlag=testDeviceConnection();
    }
    var cliJson = [{"cliName": "deviceStatus", "output": "up"}];
    postMessage(JSON.stringify(cliJson));
}

function reloadRouter(){
    getCmdOutputHandled("reload", "reload", true, true);
    var testFlag=testDeviceConnectionIos();
    while(!testFlag){
  testFlag=testDeviceConnectionIos();
    }
    var cliJson = [{"cliName": "deviceStatus", "output": "up"}];
    postMessage(JSON.stringify(cliJson));
}



function testDeviceConnection(){
  var flag="false";
  var xhr = new XMLHttpRequest();
  var loc=location.href.toString().split("ccpexp")[0];
  var file = loc+"ccpexp/version.txt";
  var randomNum = Math.round(Math.random() * 10000);
  xhr.open('GET', file+ "?rand=" + randomNum, false,"cisco","cisco");
  try {
      xhr.send();
      if (xhr.status >= 200 && xhr.status < 304) {
    flag=true;
      } else {
    flag=false;
      }
  } catch (e) {
      flag=false;
  }
  return flag;
}
function testDeviceConnectionIos(){
var flag="false";
  var xhr = new XMLHttpRequest();
  var loc=location.href.toString().split("ccpexp")[0];
  var file = loc+"ccpexp/version.txt";
  var randomNum = Math.round(Math.random() * 10000);
  xhr.open('GET', file+ "?rand=" + randomNum, false,"","");
  try {
      xhr.send();
      if (xhr.status >= 200 && xhr.status < 304) {
    flag=true;
      } else {
    flag=false;
      }
  } catch (e) {
      flag=false;
  }
  return flag;
}

function savePreferences(fileLoc,json) {
    var EMScript='event manager applet storePreferences\n'+
         'event none sync yes\n'+
         'action 1 file open LOG '+fileLoc+'preferences.JSON w+\n'+
         'action 2 file puts LOG "'+json+'"\n'+
         'action 3 file close LOG\n';
    var runScript='event manager run storePreferences\n';
    var deleteScript='no event manager applet storePreferences';
    getCmdOutputHandled("pushEM", EMScript, false, false);
    getCmdOutputHandled("runEM", runScript, true, false);
    getCmdOutputHandled("deleteEM", deleteScript, false, true);
}

function startUpgrade(dir,file,deleteTar,fileSize){
    //consoleLogMethodDetailsWrkrStart("settingsWorker.js", "startUpgrade()");
    var cliJson;
    var flashName=dir.trim().split(":")[0];
    var dirResp = getCmdOutputHandled("checkDir", "dir "+flashName+":"+file, true, false);
    var validateFlag=validateFileSize(dirResp,file,fileSize);
    if (validateFlag) {
        cliJson = [{"cliName": "checkDir", "output": validateFlag}];
        postMessage(JSON.stringify(cliJson));
        var extractDir=dir.substring(0,dir.length-6);
        var homeFileName="/home.html";
        var preferencesFileName="/preferences.JSON";
        if (extractDir.slice(-1)=="/"){
            homeFileName="home.html";
        }
        if (dir.slice(-1)=="/"){
            preferencesFileName="preferences.JSON";
        }
        getCmdOutputHandled("backupPref", "copy "+dir+preferencesFileName+" "+flashName+":", true, false);
        var deleteFolderOp=getCmdOutputHandled("deleteDir", "delete /force /recursive "+dir, true, false);
        var deleteFileOp=getCmdOutputHandled("deleteDir", "delete "+extractDir+homeFileName , true, false);
        cliJson = [{"cliName": "deleteDir", "output": deleteFolderOp+deleteFileOp}];
        postMessage(JSON.stringify(cliJson));
        getCmdOutputHandled("extractTar", "archive tar /xtract "+flashName+":"+file+" "+extractDir, true, true);
        var dirCheckResp = getCmdOutputHandled("checkXtract", "dir "+extractDir, true, false);
        var validateExtraction=checkExtraction(dirCheckResp);
        cliJson = [{"cliName": "checkXtract", "output": validateExtraction}];
        postMessage(JSON.stringify(cliJson));
        if (validateExtraction) {
            getCmdOutputHandled("restorePref", "copy "+flashName+":preferences.JSON "+dir, true, false);
            if (deleteTar){
              getCmdOutputHandled("deleteTar", "delete "+file, true, true);
            }
            cliJson = [{"cliName": "stop"}];
            postMessage(JSON.stringify(cliJson));
        }
    }else{
        cliJson = [{"cliName": "checkDir", "output": validateFlag}];
        postMessage(JSON.stringify(cliJson));
    }
    //consoleLogMethodDetailsWrkrEnd("settingsWorker.js", "startUpgrade()");
}

function startIosUpgrade(dir,file,deleteBootList,fileSize){
    //consoleLogMethodDetailsWrkrStart("settingsWorker.js", "startUpgrade()");
    var cliJson;
    var flashName=dir.trim().split(":")[0];
    var imageCheckVar=getCmdOutputHandled("imageCheck", "sh file information "+flashName+":"+file, true, false);
  if(imageCheckVar.indexOf("type is")>-1){
      cliJson = [{"cliName": "checkDir", "output": true}];
      postMessage(JSON.stringify(cliJson));
      var fileTypeLine=imageCheckVar.trim().split("\n")[1];
      var imageCheck=fileTypeLine.trim().split(" ")[2];
      if (imageCheck=="image"){
        cliJson = [{"cliName": "imageCheck", "output": "valid"}];
        postMessage(JSON.stringify(cliJson));
      }
      else{
      cliJson = [{"cliName": "imageCheck", "output": "invalid"}];
      postMessage(JSON.stringify(cliJson));

      }
    }
  else{
        cliJson = [{"cliName": "checkDir", "output": false}];
        postMessage(JSON.stringify(cliJson));
    }
    //consoleLogMethodDetailsWrkrEnd("settingsWorker.js", "startUpgrade()");
}


function startIosUpgradeViaDialog(dir,file,deleteBootList){
    //consoleLogMethodDetailsWrkrStart("settingsWorker.js", "startUpgrade()");
    var cliJson;
    var flashName=dir.trim().split(":")[0];
    if(deleteBootList){
       getCmdOutputHandled("deleteBoot", "no boot system", false, false);
       cliJson = [{"cliName": "deleteBoot"}];
       postMessage(JSON.stringify(cliJson));
      }
     if(!deleteBootList){
     bootListArray=getBootListArray();
     removeAllBoot(flashName,bootListArray);
     }
       if(flashName=="sdflash"){
       var sdFile=file.split(":")[1];
       getCmdOutputHandled("setBoot", "boot system flash:"+sdFile, false, false);
       cliJson = [{"cliName": "setBoot"}];
       postMessage(JSON.stringify(cliJson));
       }else{
       getCmdOutputHandled("setBoot", "boot system "+file, false, false);
       cliJson = [{"cliName": "setBoot"}];
       postMessage(JSON.stringify(cliJson));
       }

     if(!deleteBootList){
     reAddAllBoot(flashName,bootListArray);
      }
      getCmdOutputHandled("configReg", "config-register 0x2102", false, false);
      getCmdOutputHandled("writeMemory", "write memory", true, false);
      reloadRouter();

    //consoleLogMethodDetailsWrkrEnd("settingsWorker.js", "startUpgrade()");
}

function getBootListArray(){
  var fullBootList=getCmdOutputHandled("getList","sh run | i boot",true,false);
  var trimmedBootList=fullBootList.substring(fullBootList.indexOf("start-marker"),fullBootList.indexOf("boot-end")).replace("start-marker","").trim();
  var bootArray=trimmedBootList.split("\n");
  return bootArray;
  }
function removeAllBoot(flashName,bootArray){
  for(i=0;i<bootArray.length;i++){
    var splitLine=bootArray[i].trim();
	if(splitLine!==undefined && splitLine!=="" && splitLine!==null){
	getCmdOutputHandled("remBoot","no "+splitLine, false, false);
	}
  }
}
function reAddAllBoot(flashName,bootArray){
  for(i=0;i<bootArray.length;i++){
    var splitLine=bootArray[i].trim();
    if(splitLine!==undefined && splitLine!=="" && splitLine!==null){
    getCmdOutputHandled("addBoot",splitLine, false, false);
	}
  }
}


function checkExtraction(dirCheckResp){
    //consoleLogMethodDetailsWrkrStart("settingsWorker.js", "checkExtraction()");
    if (dirCheckResp.trim()!="") {
        var found=false;
         var splitResponse=dirCheckResp.split("\n");
        for(var i=0;i<splitResponse.length;i++){
            if (splitResponse[i].indexOf("home.html")>-1) {
                found=true;
                break;
            }
        }
    //consoleLogMethodDetailsWrkrEnd("settingsWorker.js", "checkExtraction()");
    return found;

    }else{
        //consoleLogMethodDetailsWrkrEnd("settingsWorker.js", "checkExtraction()");
        return false;
    }
}

function validateFileSize(dirResp,file,fileSize){
    //consoleLogMethodDetailsWrkrStart("settingsWorker.js", "validateFileSize()");
    var found=false,foundLine="";
    var splitResponse=dirResp.split("\n");
    for(var i=0;i<splitResponse.length;i++){
        if (splitResponse[i].indexOf(file)>-1 && splitResponse[i].indexOf("Directory of")==-1) {
            found=true;
            foundLine=splitResponse[i];
            break;
        }
    }
    if (found) {
        var trimedLine=foundLine.trim();
        //consoleLogMethodDetailsWrkrEnd("settingsWorker.js", "validateFileSize()");
        if (trimedLine!=="") {
            var splitTrim=trimedLine.split(/\s+/);
            var uploadedFileSize=parseInt(splitTrim[2]);

            if (uploadedFileSize==parseInt(fileSize)) {
                return true;
            }else{
                return false;
            }
        }else{
            return false;
        }
    }else{
        //consoleLogMethodDetailsWrkrEnd("settingsWorker.js", "validateFileSize()");
        return false;
    }

}