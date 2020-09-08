var iosVersion, licenseCheck = false, isNano = false, isEnableIPS = true, isVlanEnable = true, iosimage = "", iosk9check = "", language = "en", zoneCheck = false,preferences,advipservices=false,advsecurity=false,iosSelected="";
var isAVCSuport=false;
//var xesoftwareString="";

var showRunningConfigFormat, shRunDataLatestFlag = false, ccpExpCLICache = {}, commandsJSON;
var ccpExpressVersionValue='3.3.1';
var enableConsoleLogging=false;
var devCommCLIOutputLogging=false;
var needLandingPageAnimation=true;
var primaryWANDescription = "PrimaryWANDesc_", backupWANDescription = "BackupWANDesc_";
var clubbedCLIExecutionErrorMsg = "Clubbed CLI execution resulted in error.";
var globalCLIOutputSeparator = null, globalSeparatorAvailable = false, clubbedCLIOutputArray = null, clubbedCLIOutputAvailable = false;
var shVerFormatOdmOutput, showVerionOutput, shRunFormatOutput, shRunFormatLatest = false, shRunConfigOutput, shRunConfigLatest = false, shLicFeatureOutput;
var languageLocaleCCPExpress = "en", ipsTabHide = false, securityNotEnabled = false;
var isIRRouter = false;
var cliOutputSeparatorGeneratorCommands = 'conf t \n exit \n show version | i ---';
var defaultConfigLoadedInterfaces = false, defaultConfigLoadedIdentity = false,
  defaultConfigLoadedZones = false, defaultConfigLoadedPolicy = false,
  defaultConfigLoadedIPS = false, defaultConfigLoadedVPN = false, defaultConfigLoadedCWS = false;
var nanoPID="C841M";
var browserName="", browserVersion="";
var dmvpnHubEnableFlag=true, dmvpnSpokeEnableFlag=true;

function setGlobalCLIOutputSeparator()
{
  //consoleLogMethodDetailsStart("performChecks.js", "setGlobalCLIOutputSeparator()");
  try{
    globalCLIOutputSeparator = deviceCommunicator.getExecCmdOutput(cliOutputSeparatorGeneratorCommands);
    //consoleLog("globalCLIOutputSeparator - "+globalCLIOutputSeparator);
  } catch(e)
  {
    globalCLIOutputSeparator = '';
    //consoleLogMethodDetailsEndWithError("performChecks.js", "setGlobalCLIOutputSeparator()", e);
  }
  if (globalCLIOutputSeparator!= null && globalCLIOutputSeparator !=undefined && globalCLIOutputSeparator.trim() != '')
  {
    //if (globalCLIOutputSeparator.trim() != '')
    //{
      globalSeparatorAvailable = true;
    //}
  }
  //consoleLogMethodDetailsEnd("performChecks.js", "setGlobalCLIOutputSeparator()");
}

function consoleLog(consoleString)
{
  if (enableConsoleLogging) {
    console.log(consoleString + "\n");
  }
}

function errorLogInConsole(errString)
{
  console.log(errString + "\n");
}

function consoleLogDevComOutput(outputString) {
  if (devCommCLIOutputLogging) {
    console.log(outputString + "\n");
  }
}

function consoleLogMethodDetailsEnd(className, methodName) {
  if (enableConsoleLogging) {
    //consoleLogMethodDetails(className, methodName, "end");
  }
}

function consoleLogMethodDetailsEndWithError(className, methodName, errorMsg) {
  if (enableConsoleLogging) {
    //consoleLogMethodDetails(className, methodName, "end");
    //consoleLog(className+"-"+methodName+"-Ended with below Exception/Error:");
    console.log(errorMsg+"\n");
  }
}

function consoleLogMethodDetailsStart(className, methodName) {
  //consoleLogMethodDetails(className, methodName, "start");
}

function consoleLogEnclosingMethodDetailsStart(className, methodName) {
  //consoleLogMethodDetails(className, methodName, "start");
}

function consoleLogEnclosingMethodDetailsEnd(className, methodName) {
  //consoleLogMethodDetails(className, methodName, "end");
}

function consoleLogMethodDetails(className, methodName, startOrEnd) {
  if (enableConsoleLogging) {
    var stringToPrint = className + " - " + methodName + " - " + startOrEnd;
    console.log(stringToPrint + "\n")
    if (startOrEnd != null && startOrEnd != undefined && startOrEnd === 'start') {
      console.time(className+",Time taken for Function, " + methodName);
    } else if (startOrEnd != null && startOrEnd != undefined && startOrEnd === 'end') {
      console.timeEnd(className+",Time taken for Function, " + methodName);
    }
  }
}

function getGATrackCode() {
  (function(i, s, o, g, r, a, m) {
    i['GoogleAnalyticsObject'] = r;
    i[r] = i[r] || function() { (i[r].q = i[r].q || []).push(arguments) };
    i[r].l = 1 * new Date();
    a = s.createElement(o);
      m = s.getElementsByTagName(o)[0];
    a.async = 1;
    a.src = g;
    m.parentNode.insertBefore(a, m)
  })(window, document, 'script', '//www.google-analytics.com/analytics.js', 'ga');

  ga('create', 'UA-53950677-1', 'auto');
  ga('send', 'pageview');
}

function languageName() {
  var Lang = "e";
  //var tempLang=$.i18n.browserLang();
  //Lang="e";
  //if ((tempLang==="en-US")||(tempLang==="en")) {
  //            Lang="e";
  //}
  //else if ((tempLang==="fr-FR")||(tempLang==="fr")) {
  //            Lang="fr";
  //}
  //Lang="ja";
  $.i18n.properties({
    name: 'CCPExpNG',
    path: 'bundles/',
    language: Lang,
    mode: 'map',
    callback: function() {
    }
  });
  $.i18n.properties({
    name: 'ValidationMessages',
    path: 'bundles/',
    language: Lang,
    mode: 'map',
    callback: function() {
    }
  });
  return Lang;
}
function loadccpExpressLanguages() {
  //consoleLogMethodDetailsStart("performChecks.js", "loadccpExpressLanguages()");
  $("#mainClickForHelp").text($.i18n.prop("mainClickForHelp"));
  $("#mainClickForHelp1").text($.i18n.prop("mainClickForHelp1"));
  $("#mainViewQuickDemo").text($.i18n.prop("mainViewQuickDemo"));
  $("#display").text($.i18n.prop("display"));
  $("#hpInterfaceTitle").text($.i18n.prop("hpInterfaceTitle"));
  $("#hpInterfaceDesc").text($.i18n.prop("hpInterfaceDesc"));
  $("#hpDnsTitle").text($.i18n.prop("basicSettingsTitle"));
  $("#hpDnsDesc").text($.i18n.prop("hpDnsDesc"));
  $("#hpIdentityTitle").text($.i18n.prop("hpIdentityTitle"));
  $("#hpIdentityDesc").text($.i18n.prop("hpIdentityDesc"));
  $("#hpRoutingTitle").text($.i18n.prop("hpRoutingTitle"));
  $("#hpRoutingDesc").text($.i18n.prop("hpRoutingDesc"));
  $("#hpDiagnosisTitle").text($.i18n.prop("hpDiagnosisTitle"));
  $("#hpDiagnosisDesc").text($.i18n.prop("hpDiagnosisDesc"));
  $("#hpConfigureTitle").text($.i18n.prop("hpConfigureTitle"));
  $("#hpConfigureDesc").text($.i18n.prop("hpConfigureDesc"));
  $("#hpTroubleshootTitle").text($.i18n.prop("hpTroubleshootTitle"));
  $("#hpTroubleshootDesc").text($.i18n.prop("hpTroubleshootDesc"));
  $("#hpCliTitle").text($.i18n.prop("hpCliTitle"));
  $("#hpCliDesc").text($.i18n.prop("hpCliDesc"));
  $("#hpAdvisorTitle").text($.i18n.prop("hpAdvisorTitle"));
  $("#hpAdvisorDesc").text($.i18n.prop("hpAdvisorDesc"));
  $("#hpSecurityTitle").text($.i18n.prop("hpSecurityTitle"));
  $("#hpSecurityDesc").text($.i18n.prop("hpSecurityDesc"));
  $("#hpAclDesc").text($.i18n.prop("hpAclDesc"));
  $("#hpWiFiDesc").text($.i18n.prop("hpWiFiDesc"));
  $("#hpWiFiTitle").text($.i18n.prop("hpWiFiTitle"));
  $("#hpBasicUserTitle").text($.i18n.prop("hpBasicUserTitle"));
  $("#hpBasicUserDesc").text($.i18n.prop("hpBasicUserDesc"));
  $("#googleAnalytics").attr("title", $.i18n.prop("googleAnalyticsPopUp"));
  $("#preferencesDialog").attr("title", $.i18n.prop("menuPreference"));
  $("#analyticsInfoMessOne").text($.i18n.prop("analyticsInfoMessOne"));
  $("#analyticsInfoMessTwo").text($.i18n.prop("analyticsInfoMessTwo"));
  $("#analyticsInfoMessThree").text($.i18n.prop("analyticsInfoMessThree"));
  $("#analyticsInfoMessFour").text($.i18n.prop("analyticsInfoMessFour"));
  $("#analyticsInfoMessFive").text($.i18n.prop("analyticsInfoMessFive"));

  $('#analysisTitle').text($.i18n.prop("analysisTitle"));
  $('#ipsFeatureSupportTitle').text($.i18n.prop("ipsFeatureSupportTitle"));
  $('#recSecSettingsTitle ').text($.i18n.prop("recommendedSecuritySettings"));

  $('.switch-label').attr('data-on',$.i18n.prop("onValue"));
  $('.switch-label').attr('data-off',$.i18n.prop("offValue"));

  $('#logsTitle').text($.i18n.prop("logsTitle"));
  $('#updateTitle').text($.i18n.prop("updateTitle"));

  $("#yes").text($.i18n.prop("yes"));
  $("#no").text($.i18n.prop("no"));

  $("#basicWizardInfo").text($.i18n.prop("basicWizardInfo"));
  $("#basicQuickSetup").text($.i18n.prop("basicQuickSetup"));
  $("#basicQuickSetupInfo").text($.i18n.prop("basicQuickSetupInfo"));
  $("#basicAdvSetup").text($.i18n.prop("basicAdvSetup"));
  $("#basicAdvSetupInfo").text($.i18n.prop("basicAdvSetupInfo"));
  $(".moreOptions").text($.i18n.prop("moreOptions"));

  $('.popUpMenuItemMain[data="upgrade"] .popUpMenuText').text($.i18n.prop("ccpUpgrade"));
 $('.popUpMenuItemMain[data="updateIOS"] .popUpMenuText').text($.i18n.prop("IosUpdate"));
  $('.popUpMenuItemMain[data="reset"] .popUpMenuText').text($.i18n.prop("menuBackup"));
  $('.popUpMenuItemMain[data="preference"] .popUpMenuText').text($.i18n.prop("menuPreference"));
  $('.popUpMenuItemMain[data="caa"] .popUpMenuText').text($.i18n.prop("menuActiveAdvisor"));
  $('.popUpMenuItemMain[data="help"] .popUpMenuText').text($.i18n.prop("menuHelp"));
  $('.popUpMenuItemMain[data="feedback"] .popUpMenuText').text($.i18n.prop("menuFeedback"));

  $("div[title='Alert']").attr("title", $.i18n.prop("alertTitle"));
  //consoleLogMethodDetailsEnd("performChecks.js", "loadccpExpressLanguages()");

  $("#runningConfigBackup").attr("title", runningConfigDownloadFile(false));
}

function runningConfigDownloadFile(spacingNotNeededFlag)
{
  var runningConfigDownloadTitleString = "", runningConfigDownloadTitleSpacing = " ";

  if (spacingNotNeededFlag || languageLocaleCCPExpress == "ja") {
    runningConfigDownloadTitleSpacing = "";
  }

  runningConfigDownloadTitleString =
    $.i18n.prop("shRunConfDwnldName1") + runningConfigDownloadTitleSpacing +
    $.i18n.prop("shRunConfDwnldName2") + runningConfigDownloadTitleSpacing+
    $.i18n.prop("shRunConfDwnldName3")

  return runningConfigDownloadTitleString;
}

function loadjscssfile(filename, filetype) {
  //consoleLogMethodDetailsStart("performChecks.js", "loadjscssfile()");
  //if filename is a external JavaScript file. Else condition for filename is an external CSS file.
  if (filetype == "js") {
    var fileref = document.createElement('script')
    fileref.setAttribute("type", "text/javascript")
    fileref.setAttribute("src", filename)
  }
  else if (filetype == "css") {
    var fileref = document.createElement("link")
    fileref.setAttribute("rel", "stylesheet")
    fileref.setAttribute("type", "text/css")
    fileref.setAttribute("href", filename)
  }
  if (typeof fileref != "undefined") {
    $('head').append(fileref);
  }
  //consoleLogMethodDetailsEnd("performChecks.js", "loadjscssfile()");
}

//Changes for CCPExpress3.1PerformanceImprovement - Start

function getCommandsJSONFileURL() {
  var pageURL = $(location), urlofJSONFile;
  var varProtocol = pageURL.attr('protocol').match(/https/);

  if (varProtocol != null && varProtocol != undefined && varProtocol != '') {
    urlofJSONFile = 'https://'
  } else {
    urlofJSONFile = 'http://'
  }
  urlofJSONFile = urlofJSONFile + pageURL.attr('host') + '/' + deviceCommunicator.getInstallDir() + '/js/CachedCommands.JSON';
  return urlofJSONFile;
}

//Method to get the JSON file from the device
function getCommandsJSON() {
  return deviceCommunicator.getCommandsForCache(getCommandsJSONFileURL());
}

//Method to get the frequently used commands from the JSON file and then create a JSON object
function createCommandsJSON()
{
  //Get the JSON file and its contents
  //consoleLog("JSON cache creation start");

  var localStoreCacheString = window.localStorage.getItem('ccpExpressCache');
  if (localStoreCacheString != undefined || localStoreCacheString != null) {
    ccpExpCLICache = $.parseJSON(localStoreCacheString);
    window.localStorage.removeItem('ccpExpressCache');
  }
  else {
    //var jsonFileContents = getCommandsJSONFile();

    ////consoleLog("jsonFileContents - "+jsonFileContents);

    //Create commandsJSON object
    //commandsJSON = $.parseJSON(jsonFileContents);
    commandsJSON = getCommandsJSON();
    //consoleLog("commandsJSON received - " + JSON.stringify(commandsJSON));

    var cacheIndex = 0;
    //consoleLog("looping throug jSON object starts");
    //Loop through the whole JSON object, take the commands, execute them and store in cache.
    $.each(commandsJSON, function(cmdKey, cliValue) {
      var cmdCacheLatestFlag = true, reloads = 0, reads = 0, reloadInProgress = false, dataLoadSuccess = true, cli = cliValue.Command;
      //consoleLog("adding the command " + cli);
      if (cli.indexOf("deviceCommunicator.getInstallDir()") > -1) {
        cli = cli.replace("deviceCommunicator.getInstallDir()", deviceCommunicator.getInstallDir());
      }
      //consoleLog("direct access to command -" + commandsJSON[cacheIndex]["Command"]);
      var cliOutputValue = "";
      try {
        cliOutputValue = deviceCommunicator.getExecCmdOutput(cli);
        ccpExpCLICache[cli] = {
                                "CLI": cli,
                                "CLIOutput": cliOutputValue,
                                "Latest": cmdCacheLatestFlag,
                                "Reloads": reloads,
                                "Reads": reads,
                                "ReloadInProgress": reloadInProgress,
                                "DataLoadSuccess": dataLoadSuccess};
      }
      catch (e) {
        cliOutputValue = "";
      }


      cacheIndex++;
    });

    moveCacheToLocalStorage();
    ////consoleLog("Cached Commands:" + JSONString);
//  getCacheAccessDetails();
  }
}

function initiateCacheReload(templateName)
{
  reloadShowRunData();
}

function evaluateCacheReload(templateName)
{
  markShowRunDataAsStale();
}
/*
function getCacheAccessDetails()
{
  //consoleLog("PRINTING CACHE START");
  //Gets the read/write counts of all the cached commands and status of the CLLI output stored
  $(ccpExpCLICache).each(function(i, val)
  {
    $.each(val, function(key, val)
    {
      //consoleLog("CLI: " + key + ", IsLatest-" + val["Latest"] + ", #ofReloads-" + val["Reloads"] + ", #ofReads-" + val["Reads"]);
    });
  });
  //consoleLog("PRINTING CACHE DONE");
}
*/
function getCacheCLIAccessDetails(cliJSONEntry)
{
  if (cliJSONEntry != null && cliJSONEntry != undefined) {
    //consoleLog("CLI: " + cliJSONEntry["CLI"] + ", IsLatest-" + cliJSONEntry["Latest"] + ", #ofReloads-" + cliJSONEntry["Reloads"] + ", #ofReads-" + cliJSONEntry["Reads"]);
  }
}

//Method gets the cached CLI output if latest. If not, it loads the latest into cache and returns the same.
function getCommandInCache(cliString)
{
  var commandOutput;
  commandOutput = ccpExpCLICache[cliString];
  return commandOutput;
}

function getCommandInLocalStorage(cliString)
{
  var localStoreCacheString = window.localStorage.getItem('ccpExpressCache');
  var tempCacheObject;
  if (localStoreCacheString != undefined || localStoreCacheString != null) {
    tempCacheObject = $.parseJSON(localStoreCacheString);
  }
  return tempCacheObject[cliString];
}

function markCachedCLIOutputLoadFailed(cliString) {
  var commandInCache = ccpExpCLICache[cliString];
  if (commandInCache != undefined && commandInCache != null) {
    commandInCache["DataLoadSuccess"] = false;
  }
  var JSONString = JSON.stringify(ccpExpCLICache);
  window.localStorage.setItem('ccpExpressCache', JSONString);
}

function markCachedCLIOutputAsStale(cliString) {
  var commandInCache = ccpExpCLICache[cliString];
  if (commandInCache != undefined && commandInCache != null) {
    markCachedCLIOutputObjectAsStale(commandInCache);
  }
}

function moveCacheToLocalStorage()
{
  var JSONString = JSON.stringify(ccpExpCLICache);
  window.localStorage.setItem('ccpExpressCache', JSONString);
}

function markCachedCLIOutputObjectAsStale(cliObjectInCache)
{
  cliObjectInCache["Latest"] = false;
  //moveCacheToLocalStorage();
}

function asynchronousCLICaching() {
  //Loop through the cache
  //Find any CLIOutput is marked with Latest flag as false.
  //If so, execute the command and put the latest data in.
}

function synchronousRefreshCLIOutputInCacheForCLIString(cliString)
{
  var commandInCache = ccpExpCLICache[cliString];
  if (commandInCache != undefined && commandInCache != null) {
    commandInCache["Latest"] = false;
    commandInCache["ReloadInProgress"] = true;
    commandInCache["DataLoadSuccess"] = false;
    commandInCache["CLIOutput"] = deviceCommunicator.getExecCmdOutput(cliString);
    commandInCache["Reloads"] = commandInCache["Reloads"] + 1;
    commandInCache["ReloadInProgress"] = false;
    commandInCache["DataLoadSuccess"] = true;
    commandInCache["Latest"] = true;
  }
  //moveCacheToLocalStorage();
  return commandInCache;
}

function synchronousRefreshCLIOutputInCache(commandInCache)
{
  if (commandInCache != undefined && commandInCache != null) {
    commandInCache["Latest"] = false;
    commandInCache["ReloadInProgress"] = true;
    commandInCache["DataLoadSuccess"] = false;
    commandInCache["CLIOutput"] = deviceCommunicator.getExecCmdOutput(commandInCache["CLI"]);
    commandInCache["Reloads"] = commandInCache["Reloads"] + 1;
    commandInCache["ReloadInProgress"] = false;
    commandInCache["DataLoadSuccess"] = true;
    commandInCache["Latest"] = true;
  }
  //moveCacheToLocalStorage()
  return commandInCache;
}

function markShowRunDataAsStale() {
  //markCachedCLIOutputAsStale("show running-config | format");
  //markCachedCLIOutputAsStale("show running-config");
}

function reloadShowRunData()
{
  //synchronousRefreshCLIOutputInCacheForCLIString("show running-config | format");
  //synchronousRefreshCLIOutputInCacheForCLIString("show running-config");
  //synchronousRefreshCLIOutputInCacheForCLIString("show running-config | include ip route");
}




function getOneTimeUsers() {
  //consoleLogMethodDetailsStart("performChecks.js", "getOneTimeUsers()");
  loadjscssfile("../js/deviceCommunicator.js", "js");

  //Changes for CCPExpress3.1PerformanceImprovement
  //Loading the cache upon page load. This has to be done after device communicator is loaded.
  //createCommandsJSON();
  if (!globalSeparatorAvailable) {
    setGlobalCLIOutputSeparator();
  }

  var cliArray = [];
  cliArray.push("show version | format " + deviceCommunicator.getInstallDir() + "/odm/overviewshVer.odm");
  cliArray.push(cliOutputSeparatorGeneratorCommands);
  cliArray.push("show running-config | format");
  cliArray.push(cliOutputSeparatorGeneratorCommands);
  cliArray.push("show run | i licensefeature");
  cliArray.push(cliOutputSeparatorGeneratorCommands);
  cliArray.push("show run | i zone ");

  cliArray.push(cliOutputSeparatorGeneratorCommands);
  cliArray.push("show run | i licenseudi");
  cliArray.push(cliOutputSeparatorGeneratorCommands);
  cliArray.push("show ip interface brief ");
  cliArray.push(cliOutputSeparatorGeneratorCommands);
  cliArray.push("show version");
  cliArray.push(cliOutputSeparatorGeneratorCommands);
  cliArray.push("show running-config");


/*
  cliArray.push(cliOutputSeparatorGeneratorCommands);
  cliArray.push("show flow record nbar-appmon");
  cliArray.push(cliOutputSeparatorGeneratorCommands);
  cliArray.push("show flow monitor application-mon");
*/

/*
  //Commenting out unwanted push to CLI Array.
  //In future, if any more CLIs are to be considered, please ensure to add those here.
  cliArray.push(cliOutputSeparatorGeneratorCommands);
  cliArray.push();
  cliArray.push(cliOutputSeparatorGeneratorCommands);
  cliArray.push();
  cliArray.push(cliOutputSeparatorGeneratorCommands);
  cliArray.push();
  cliArray.push(cliOutputSeparatorGeneratorCommands);
*/

  clubbedCLIOutputArray = deviceCommunicator.clubShowCmdsExecuteAndSplitOutput(cliArray, globalCLIOutputSeparator);

  if (clubbedCLIOutputArray != null && clubbedCLIOutputArray.length >0) {
    clubbedCLIOutputAvailable = true;
    shVerFormatOdmOutput = clubbedCLIOutputArray[0];
    shRunFormatOutput = clubbedCLIOutputArray[1];
    shRunFormatLatest = true;
    //shLicFeatureOutput = clubbedCLIOutputArray[2];
    showVerionOutput = clubbedCLIOutputArray[6];
    shRunConfigOutput = clubbedCLIOutputArray[7];
    shRunConfigLatest = true;
  }

  var xml,
    oneTimeUsers = [],
    encrypted,
    password,
    privilegelevel,
    user,
    version,
    ver,
    verOnlyNo,
    href = $(location).attr('href');

  try {

    //snort implementation
    /*xml = deviceCommunicator.getExecCmdOutput("show version | format " + deviceCommunicator.getInstallDir() + "/odm/overviewshVer.odm");
    version = $(xml).find('Version').text();
    xesoftwareString=$(xml).find('IOS-XE').text();
    ver = parseFloat(version);
    verOnlyNo = ver.toFixed(1);
    iosVersion = verOnlyNo;
    var patt1 = /^[-+]?[0-9]+\.[0-9]+$/g;
    iosimage = $(xml).find('Software').text();
    if (xesoftwareString!="") {
      xml = deviceCommunicator.getExecCmdOutput("show version");
      newline = xml.split("\n");
      for(n=0;n<newline.length;n++){
        if (newline[n].indexOf("Version")>-1) {
          versonsplit=newline[n].split("Version")[1];
          var inputString=versonsplit.trim().split(" ");
          if (n>=1&&parseFloat(inputString[0]).toString().match(patt1)) {
            ver = parseFloat(inputString[0]);
    verOnlyNo = ver.toFixed(1);
    iosVersion = verOnlyNo;
          }
        }
      }

    }*/
    if (clubbedCLIOutputAvailable && shVerFormatOdmOutput != null) {
      xml = shVerFormatOdmOutput;
    }
    else {
      xml = deviceCommunicator.getExecCmdOutput("show version | format " + deviceCommunicator.getInstallDir() + "/odm/overviewshVer.odm");
    }
    version = $(xml).find('Version').text();
    ver = parseFloat(version);
    verOnlyNo = ver.toFixed(1);
    iosVersion = verOnlyNo;
    iosimage = $(xml).find('Software').text();
  }
  catch (error) {

    versionAlertBox();
  }
  if ((href.indexOf("ccpExpress.html") !== -1 || href.indexOf("endUserView.html") !== -1) && iosVersion < 15.2) {

    /**************** condition to check router IOS version *****************/
    //if (iosVersion < 15.2) {

      versionAlertBox();

    //}


  }

  /******************************Pop UP for One Time User **********************************/

  if (clubbedCLIOutputAvailable && shRunFormatOutput != null && shRunFormatLatest) {
      xml = shRunFormatOutput;
    }
  else {
    xml = deviceCommunicator.getExecCmdOutput("show running-config | format");
  }

  $(xml).find('username').each(function() {
    encrypted = false;
    user = $(this).find('UserName').text();
    privilegelevel = $(this).find('UserPrivilegeLevel').text();
    if (privilegelevel === "") {
      privilegelevel = 1;
    }
    $(this).find('one-time').each(function() {
      $(this).find('password').each(function() {
        password = $(this).find('UnencryptedUserPassword').text();
        oneTimeUsers.push({userName: user, password: password, encrypt: encrypted, privilege: privilegelevel});
      });
      $(this).find('secret').each(function() {
        password = $(this).find('HiddenUserSecretString').text();
        encrypted = true;
        oneTimeUsers.push({userName: user, password: password, encrypt: encrypted, privilege: privilegelevel});
      });
    });

  });
  //consoleLogMethodDetailsEnd("performChecks.js", "getOneTimeUsers()");
  return oneTimeUsers;
}

function showOneTimeUser(userNumber, oneTimeUsers) {
  //consoleLogMethodDetailsStart("performChecks.js", "showOneTimeUser()");
  loadjscssfile("../external/development-bundle/themes/flick/jquery-ui-1.8.17.custom.css1", "css");
  //loadAndDisplayLanguages();
  $("#oneTimeUSer-dialogForm").dialog("open");
  $('#oneTimeUSer-dialogForm').append('<div id="oneTimeUserError" class="ui-state-error ui-corner-all" style="padding: 0 .7em;"><p><span  class="ui-icon ui-icon-alert" style="float: left; margin-right: .3em;"></span><span id="oneTimeUserErrorMessage"></span></p></div>');
  $('#oneTimeUSer-dialogForm').append('<form id="oneTimeUserForm" method="get" action=""></form>');
  $('#oneTimeUserForm').append('<table id="onetimeUserTable"></table>');
  $('#onetimeUserTable').append('<tr><td>' + $.i18n.prop("oneTimeUserName") + '</td><td><input type="text" name="username" id="oneTimeUserInput" class="required changeUser"/></td></tr>');
  $('#onetimeUserTable').append('<tr><td>' + $.i18n.prop("oneTimePswd") + '</td><td><input type="password" name="password" id="paassworInput" class="required" minlength="1" maxlength = "25"/></td></tr>');
  $('#onetimeUserTable').append('<tr><td>' + $.i18n.prop("oneTimeConfirmPswd") + '</td><td><input type="password" name="confirmpassword" id="confirmInput" class="required" minlength="1" maxlenght = "25"equalTo="#paassworInput"/></td></tr>');
  $('#onetimeUserTable').append('<tr style="display:none"><td>' + $.i18n.prop("oneTimePrivelege") + '</td><td><select name="privileges" id="privileges"></select></td></tr>');
  $('#privileges').append('<option>1</option>');
  $('#privileges').append('<option>2</option>');
  $('#privileges').append('<option>3</option>');
  $('#privileges').append('<option>4</option>');
  $('#privileges').append('<option>5</option>');
  $('#privileges').append('<option>6</option>');
  $('#privileges').append('<option>7</option>');
  $('#privileges').append('<option>8</option>');
  $('#privileges').append('<option>9</option>');
  $('#privileges').append('<option>10</option>');
  $('#privileges').append('<option>11</option>');
  $('#privileges').append('<option>12</option>');
  $('#privileges').append('<option>13</option>');
  $('#privileges').append('<option>14</option>');
  $('#privileges').append('<option selected>15</option>');
  $('#privileges').hide();
  $('#oneTimeUserError').hide();
  $("#oneTimeUSer-dialogForm").dialog().dialog("widget").find(".ui-dialog-titlebar-close").hide();
  $('<p id = "oneTimeUserInfo" style="color: blue"></p>').html($.i18n.prop("NoteUsername") + ' ' + oneTimeUsers[userNumber].userName + " " + $.i18n.prop("oneTimeUserMessage")).prependTo('#oneTimeUserForm');
  $("#oneTimeUSer-dialogForm").dialog("option", "title", $.i18n.prop("oneTimeUserTitle"));
  $('#oneTimeUserInput').val("");
  $('#paassworInput').val("");
  $('#confirmInput').val("");
  $('#privileges').val(oneTimeUsers[userNumber].privilege);
  //consoleLogMethodDetailsEnd("performChecks.js", "showOneTimeUser()");
}
function checkForNanoDevice(liceUid) {
  //consoleLogMethodDetailsStart("performChecks.js", "checkForNanoDevice()");
  try {
    var found = false;
    resp = liceUid;
    //deviceCommunicator.getExecCmdOutput("show license udi");
    licenseSplit = resp.split("\n");
    for (var i = 1; i < licenseSplit.length; i++) {
      var licenseDetails = licenseSplit[i].split(/\s+/);
       var startReg=new RegExp('^' + nanoPID, 'i');
      if ((licenseDetails[1].trim() == "CISCO414R-K9") || (licenseDetails[1].trim() == "CISCO418R-K9") || (licenseDetails[1].trim() == "WIM-3G") || (licenseDetails[1].trim() == "WIM-1T") ||  startReg.test(licenseDetails[1].trim())) {
        found = true;
        break;
      }
    }
    //consoleLogMethodDetailsEnd("performChecks.js", "checkForNanoDevice()");
    return found;
  } catch (error) {
    errorLogInConsole("Error in checkForNanoDevice()");
    //consoleLogMethodDetailsEndWithError("performChecks.js", "checkForNanoDevice()",error);
    return found;
  }
}

function isVlanCheckEnable(){
    try{
        var check = false,response;
        response = deviceCommunicator.getConfigCmdOutput("interface vlan?");
    }catch(error){
        var respOutput = error.errorResponse;
        if(respOutput == "Vlan"){
                  check = true;
          return check;
        } else {
          return check;
        }
    }
}

function isIPSEnableForDevice(liceUid) {
  //consoleLogMethodDetailsStart("performChecks.js", "isIPSEnableForDevice()");
  try {
    var found = true;
    resp = liceUid;
    licenseSplit = resp.split("\n");
    for (var i = 1; i < licenseSplit.length; i++) {
      var licenseDetails = licenseSplit[i].split(/\s+/);
       var startReg=new RegExp('^' + nanoPID+"-4X".trim(), 'i');
      if ((licenseDetails[1].trim() == "CISCO414R-K9") || (startReg.test(licenseDetails[1].trim()))) {
        found = false;
        break;
      }
    }
    //consoleLogMethodDetailsEnd("performChecks.js", "isIPSEnableForDevice()");
    return found;
  } catch (error) {
    //consoleLogMethodDetailsEndWithError("performChecks.js", "isIPSEnableForDevice()",error);
    return found;
  }
}

function check860device(versionCheckOutput) {
  //consoleLogMethodDetailsStart("performChecks.js", "check860device()");
  //code
  var platformType;
  if (clubbedCLIOutputAvailable && versionCheckOutput != null) {
    platformType = deviceCommunicator.getPlatformTypeFromShowVersionOutput(versionCheckOutput);
  }
  else {
    platformType = deviceCommunicator.getPlatformType();
  }

  var returnValue;
  if ((iosimage.toLowerCase().indexOf("k9") > -1 && iosVersion < 15.5) && (platformType.indexOf('867') != -1 || platformType.indexOf('866') != -1)) {
    returnValue = "staticNatEnable";
  } else if ((iosimage.toLowerCase().indexOf("k9") > -1 && iosVersion >= 15.5) && (platformType.indexOf('867') != -1 || platformType.indexOf('866') != -1)) {
    zoneCheck = checkZone();
    returnValue = "SecurityEnable";
  } else {
    returnValue = "nothing";
  }
  //consoleLogMethodDetailsEnd("performChecks.js", "check860device()");
  return returnValue;

}

function checkZone(shZoneSecurityCLIOutput) {
  //consoleLogMethodDetailsStart("performChecks.js", "checkZone()");
  var checkZoneReturnValue = false;
  try {
    var reg = new RegExp("[,\\n]");
    var cliOutputcheck;
    //if (clubbedCLIOutputAvailable &&  shZoneSecurityCLIOutput!= null) {
    //  cliOutputcheck = shZoneSecurityCLIOutput;
    //}
    //else {
      cliOutputcheck = deviceCommunicator.getExecCmdOutput("show zone security");
    //}
    var rowscheck = cliOutputcheck.split(reg);
    var countzone = 0;

    for (var i = 0; i < rowscheck.length; i++) {
      if (rowscheck[i].indexOf("zone WAN") > -1 || rowscheck[i].indexOf("zone VPN") > -1 || rowscheck[i].indexOf("zone DMZ") > -1 || rowscheck[i].indexOf("zone LAN") > -1) {

        countzone = countzone + 1;

      }
    }

    cliOutputcheckflowrecord = deviceCommunicator.getExecCmdOutput("show flow record nbar-appmon");
    cliOutputcheckflowmoniter = deviceCommunicator.getExecCmdOutput("show flow monitor application-mon");
    //consoleLogMethodDetailsEnd("performChecks.js", "checkZone()");
    if (countzone >= 4) {
      checkZoneReturnValue = true;
    } else {
      checkZoneReturnValue = false;
    }
  } catch (error) {
    //consoleLogMethodDetailsEndWithError("performChecks.js", "checkZone()",error);
    checkZoneReturnValue = false;
  }
  return checkZoneReturnValue;
}
function checkSecurityLicense() {
  //consoleLogMethodDetailsStart("performChecks.js", "checkSecurityLicense()");
  var checkSecurityLicenseReturnValue = false;

  try {
    var found = false;

    //if (clubbedCLIOutputAvailable &&  shLicFeatureOutput!= null) {
    //  resp = shLicFeatureOutput;
    //}
    //else {
      resp = deviceCommunicator.getExecCmdOutput("show license feature");
    //}

    licenseSplit = resp.split("\n");
    for (var i = 1; i < licenseSplit.length; i++) {
      var licenseDetails = licenseSplit[i].split(/\s+/);
      if ((licenseDetails[0].trim()=="securityk9" && licenseDetails[4].trim().toLowerCase()=="yes") ||(licenseDetails[0].trim()=="seclitek9" && licenseDetails[4].trim().toLowerCase()=="yes") || (licenseDetails[0].trim()=="advipservices" && licenseDetails[4].trim().toLowerCase()=="yes") || (licenseDetails[0].trim()=="advsecurity" && licenseDetails[4].trim().toLowerCase()=="yes")) {
            found=true;
            if(licenseDetails[0].trim()=="advsecurity" && licenseDetails[4].trim().toLowerCase()=="yes"){
                advsecurity=true;
            }
            if((licenseDetails[0].trim()=="advipservices" && licenseDetails[4].trim().toLowerCase()=="yes")){
                advipservices=true;
            }
        break;
      }
    }

    //consoleLogMethodDetailsEnd("performChecks.js", "checkSecurityLicense()");
    if (found && iosVersion > 15.4) {
      checkSecurityLicenseReturnValue = true; }
    else {
      checkSecurityLicenseReturnValue = false; }
  }
  catch (error) {
    checkSecurityLicenseReturnValue = false;
  }
  return checkSecurityLicenseReturnValue;
}

function initializePreferenceToolTips(){
    //consoleLogMethodDetailsStart("performChecks.js", "initializePreferenceToolTips()");
    $('#analysisTitle').siblings( ".fa-question-circle" ).tooltip({items: "em", content: $.i18n.prop("analysisDesc"), track: true, tooltipClass: 'tooltipNano'});
    $('#ipsFeatureSupportTitle').siblings( ".fa-question-circle" ).tooltip({items: "em", content: $.i18n.prop("ipsFeatureSupportDesc"), track: true, tooltipClass: 'tooltipNano'});
    $('#recSecSettingsTitle').siblings( ".fa-question-circle" ).tooltip({items: "em", content: $.i18n.prop("ciscoRecomSettings"), track: true, tooltipClass: 'tooltipNano'});
    $('#updateTitle').siblings( ".fa-question-circle" ).tooltip({items: "em", content: $.i18n.prop("updateDesc"), track: true, tooltipClass: 'tooltipNano'});
    $('#logsTitle').siblings( ".fa-question-circle" ).tooltip({items: "em", content: $.i18n.prop("logsDesc"), track: true, tooltipClass: 'tooltipNano'});
    //consoleLogMethodDetailsEnd("performChecks.js", "initializePreferenceToolTips()");
}

function loadPreferences(){
    //consoleLogMethodDetailsStart("performChecks.js", "loadPreferences()");
    if (languageLocaleCCPExpress == "ja" && !securityNotEnabled) {
          $('#ipsJapDisable').show();
    }
    var securitySettingsEnabled = true, secSetCmdOuput, tempHolder;
    secSetCmdOuput = deviceCommunicator.getExecCmdOutput("show run | i service password-encryption");
    if (secSetCmdOuput!= null && secSetCmdOuput != undefined && secSetCmdOuput != "") {
      var commandOutputArray =secSetCmdOuput.split(/\s+/);
      if (commandOutputArray[0] == "no") {
        securitySettingsEnabled = false;
      }
      else {
        securitySettingsEnabled = true;
      }
    } else
    {
      securitySettingsEnabled = false;
    }
    
    preferences=deviceCommunicator.getCommandsForCache("../preferences.JSON");
    if (preferences!=null && preferences!=undefined) {
        if (preferences.analytics) {
            $('#analyticsCheck').prop("checked",true);
        }else{
            $('#analyticsCheck').prop("checked",false);
        }
        if (preferences.japIPSEnable) {
            $('#ipsFeatureJapDisableCheck').prop("checked",true);
                        if (languageLocaleCCPExpress == "ja") {
                          ipsTabHide = false;
                        }
        }else{
            $('#ipsFeatureJapDisableCheck').prop("checked",false);
                        if (languageLocaleCCPExpress == "ja") {
                          ipsTabHide = true;
                        }
        }

        if (securitySettingsEnabled && preferences.recmndSecrtySettings) {
            $('#recommmendedSecuritySettingsCheck').prop("checked",true);
        } else if (securitySettingsEnabled) {
            $('#recommmendedSecuritySettingsCheck').prop("checked",true);
        }
        else{
            $('#recommmendedSecuritySettingsCheck').prop("checked",false);
        }

        if (preferences.updates) {
            $('#updatesCheck').prop("checked",true);
        }else{
            $('#updatesCheck').prop("checked",false);
        }
        if (preferences.logs) {
            $('#logsCheck').prop("checked",true);
        }else{
            $('#logsCheck').prop("checked",false);
        }
    }else{
            $('#analyticsCheck').prop("checked",false);
            $('#ipsFeatureJapDisableCheck').prop("checked", false);
            $('#recommmendedSecuritySettingsCheck').prop("checked", false);
            $('#updatesCheck').prop("checked",false);
            $('#logsCheck').prop("checked",false);
    }
    $('#logsOption').hide();
    //consoleLogMethodDetailsEnd("performChecks.js", "loadPreferences()");
}

function getChangedPreferences(analyticsOpened){
    var json="";
    if (preferences!=null && preferences!=undefined) {
        if ($('#analyticsCheck').is(':checked')) {
            preferences.analytics=true;
        }else{
            preferences.analytics=false;
        }
        if ($('#ipsFeatureJapDisableCheck').is(':checked')) {
            preferences.japIPSEnable=true;
                        if (languageLocaleCCPExpress == "ja") {
                          ipsTabHide = false;
                        }
        }else{
                  console.log("japIPSEnable to false in getChangedPreferences");
            preferences.japIPSEnable=false;
                        if (languageLocaleCCPExpress == "ja") {
                          ipsTabHide = true;
                        }
        }

        if ($('#recommmendedSecuritySettingsCheck').is(':checked')) {
            preferences.recmndSecrtySettings=true;
        }else{
            preferences.recmndSecrtySettings=false;
        }

        if ($('#updatesCheck').is(':checked')) {
            preferences.updates=true;
        }else{
            preferences.updates=false;
        }
        if ($('#logsCheck').is(':checked')) {
            preferences.logs=true;
        }else{
            preferences.logs=false;
        }
        if (analyticsOpened) {
            preferences.analyticsOpened=true;
        }
        json='{\\"analytics\\":'+preferences.analytics+',\\"japIPSEnable\\":'+preferences.japIPSEnable+',\\"recmndSecrtySettings\\":'+preferences.recmndSecrtySettings+',\\"updates\\":'+preferences.updates+',\\"logs\\":'+preferences.logs+',\\"analyticsOpened\\":'+preferences.analyticsOpened+'}';
    }else{

        json='{\\"analytics\\":false,\\"japIPSEnable\\":false,\\"recmndSecrtySettings\\":false,\\"updates\\":false,\\"logs\\":false,\\"analyticsOpened\\":false}';
    }
    return json;
}

function checkPreferencesChange(){
    var flag=false;
    if ($('#analyticsCheck').is(':checked') != preferences.analytics) {
            flag=true;
    }
    else if ($('#ipsFeatureJapDisableCheck').is(':checked') != preferences.japIPSEnable) {
            flag=true;
    }
    else if ($('#recommmendedSecuritySettingsCheck').is(':checked') != preferences.recmndSecrtySettings) {
            flag=true;
    }
    else if ($('#updatesCheck').is(':checked') != preferences.updates) {
            flag=true;
    }
    else if ($('#logsCheck').is(':checked') != preferences.logs) {
            flag=true;
    }
    return flag;
}

function storePreferences(json){
    //consoleLogMethodDetailsStart("performChecks.js", "loadPreferences()");
    var fileLoc=deviceCommunicator.getInstallDir();
    if (fileLoc.slice(-1)!="/"){
        fileLoc=fileLoc+"/";}

    /*var EMScript='event manager applet storePreferences\n'+
             'event none sync yes\n'+
             'action 1 file open LOG '+fileLoc+'preferences.JSON w+\n'+
             'action 2 file puts LOG "'+json+'"\n'+
             'action 3 file close LOG\n';
    var runScript='event manager run storePreferences\n';
    var deleteScript='no event manager applet storePreferences';
    deviceCommunicator.getConfigCmdOutput(EMScript);
    deviceCommunicator.getExecCmdOutput(runScript);
    deviceCommunicator.getConfigCmdOutput(deleteScript);*/
    var messagePost = [{
        "name": "preferences",
        "fileLoc": fileLoc,
        "json": json
    }];
    worker.postMessage(JSON.stringify(messagePost));
    worker.onmessage = function(event) {
        var resp = JSON.parse(event.data);
        if (resp[0]['cliName'] == "deleteEM") {
            loadPreferences();
            worker.terminate();
        }
    };

    //consoleLogMethodDetailsEnd("performChecks.js", "loadPreferences()");
}


//On window loaded
window.onload=function(){
    setTimeout(function(){
        if (!preferences.analyticsOpened) {
            worker = new Worker('../js/settingsWorker.js');
            $("#googleAnalytics").dialog("open");
        }
    },2000);

}

/***********************To do Internationalization***********************************/


$(document).ready(function() {
  $('#topnav-10').hide();
  $('#topnav-11').hide();
  languageName();
  languageLocaleCCPExpress = $.i18n.prop("langwage");
  if (languageLocaleCCPExpress == "ja") {
    ipsTabHide = true;
  }


  loadccpExpressLanguages();
  $("#ccpHome").removeClass("backgroundColor");
  $('#ccpHome').show();
  $('.bubble').hide();
  $('#maincontent').show();
  var oneTimeUsers = [],
    NonOneTimeUsers = 0;
  oneTimeUsers = getOneTimeUsers();
  var xml;
  //var interfaceType, visible = false; $("#mainFadeInbox").hide().slideDown();

  var arrval = [], ccpexpVersion;
  if (ccpExpressVersionValue!= "ccpexpressTextversion") {
    ccpexpVersion = ccpExpressVersionValue;
  } else {
    readVal = deviceCommunicator.readFromTemplate("version.txt", arrval, true);
    versionText = readVal.split(/\s+/);
    ccpexpVersion = versionText[2];
  }
  //$('.popUpMenuVersion').text(($.i18n.prop("version") + " " + ccpexpVersion));
  $('#versionText').text($.i18n.prop("version"));
  $('#versionNoText').text(ccpexpVersion);


  licenseCheck = checkSecurityLicense();
  if (!licenseCheck) {
    iosk9check = check860device(showVerionOutput);
    if (iosk9check == "SecurityEnable" || iosk9check == "staticNatEnable") {
      //code
      $('#topnav-11').show();
    } else {
      $('#topnav-11').hide();
      securityNotEnabled = true;
    }
  }
  else {
    $('#topnav-11').show();
  }
  var licenseUid = "";
  try {

    //if (clubbedCLIOutputAvailable) {
    //  licenseUid = clubbedCLIOutputArray[4];
    //}
    //else {
      licenseUid = deviceCommunicator.getExecCmdOutput("show license udi");
    //}


    isNano = checkForNanoDevice(licenseUid);
    isEnableIPS = isIPSEnableForDevice(licenseUid);
    isVlanEnable = isVlanCheckEnable();
    //dmvpnHubEnableFlag=false;
    //dmvpnSpokeEnableFlag = false;
    dmvpnHubEnableFlag=isDmvpnHubEnabledForDevice(licenseUid);
    dmvpnSpokeEnableFlag = isDmvpnSpokeEnabledForDevice(licenseUid);
  } catch (error) {
    licenseUid = "";
  }

  $.browser.chrome = /chrome/.test(navigator.userAgent.toLowerCase());
  if ($.browser.chrome) {
    $('ul#topnav li').find('a').each(function() {
      //$(this).css("z-index","1");
    });
  }

  /*$("#feedback").hover(function() {
    $("#display").slideDown(500);
  }, function() {
    $("#display").slideUp();
  });*/
  $('#moreMenuOptionsMain').click(function(){
    $('.popUpMenuDiv').fadeToggle("fast",function() {
    $(this).css("overflow","visible");
    });
  });

  $('#runningConfigDownload').click(function(){
          var cli=getRunningConfigOutput();
          //Based on Japanese team feedback during demo, the file name should be in English
          //createConfig(cli,runningConfigDownloadFile(true),".txt");
          createConfig(cli,"RunningConfigBackup",".txt");
  });

  $('body').click(function(e){
    var target = $(e.target).parent();
    if ($(this).find('#moreMenuOptionsMain').length>0 && !$('.popUpMenuDivMain').is(':hidden') && !target.is('a#moreMenuOptionsMain') && target.parents('.popUpMenuDivMain').length==0 && !target.is('.popUpMenuDiv')) {
        $('.popUpMenuDiv').fadeToggle();
    }
    if ($(this).find('#moreMenuOptions').length>0 && !$('.popUpMenuDiv').is(':hidden') && !target.is('a#moreMenuOptions') && target.parents('.popUpMenuDiv').length==0 && !target.is('.popUpMenuDiv')) {
        $('.popUpMenuDiv').fadeToggle();
    }
  });
  $('.popUpMenuItemMain').click(function(){
    $('.popUpMenuDiv').fadeToggle();
    if ($(this).attr("data")=="upgrade") {
    var loc=window.location.href.toString();
    var splitLoc=loc.split("/html/");
    window.location.replace(splitLoc[0]+"/html/frames.html?feature=upgradeCCP");
    }else if ($(this).attr("data")=="updateIOS") {
    var loc=window.location.href.toString();
    var splitLoc=loc.split("/html/");
    window.location.replace(splitLoc[0]+"/html/frames.html?feature=upgradeIOS");
    }else if ($(this).attr("data")=="feedback") {
    window.open("https://www.ciscofeedback.vovici.com/se.ashx?s=6A5348A77E0CDC49");
    }else if ($(this).attr("data")=="help") {
    window.open("http://www.cisco.com/c/en/us/td/docs/net_mgmt/cisco_configuration_professional_express/v3_3/guides/featureguide/ccp_express_Feature_Guide.html");
    }else if ($(this).attr("data")=="caa") {
    var loc=window.location.href.toString();
    var splitLoc=loc.split("/html/");
    window.location.replace(splitLoc[0]+"/html/frames.html?feature=phonehome");
    }else if ($(this).attr("data")=="preference") {
    $('#preferencesDialog').dialog("open");
    worker = new Worker('../js/settingsWorker.js');
    }else if ($(this).attr("data")=="reset") {
    var loc=window.location.href.toString();
    var splitLoc=loc.split("/html/");
    window.location.replace(splitLoc[0]+"/html/frames.html?feature=reset");
    }
    });

    if (clubbedCLIOutputAvailable) {
      xml = clubbedCLIOutputArray[5];
    }
    else {
      xml = deviceCommunicator.getExecCmdOutput("show ip interface brief");
    }



  if (xml.toLowerCase().indexOf('wlan') !== -1 || xml.toLowerCase().indexOf('wlan') !== -1) {
    $('#topnav-10').show();
  }
  loadPreferences();
  initializePreferenceToolTips();
  $("#preferencesDialog").dialog({
    autoOpen: false,
    height: 490,
    width: 675,
    modal: true,
    buttons: [{
        text: $.i18n.prop("ok"),
        click: function() {
          $(this).dialog("close");
        }
      }],
    close: function() {
      var check=checkPreferencesChange();
      if (check) {
        var json=getChangedPreferences();
        storePreferences(json);
        if (ipsTabHide) {
          $("#ipsTab").hide();
          var activeTabIdx = $("#utmTabs").tabs("option","active");
          if(activeTabIdx != null && activeTabIdx != undefined)
          {
            var selector = '#utmTabs > ul > li';
            var activeTab = $(selector).eq(activeTabIdx).attr('id');
            if(activeTab != null && activeTab != undefined && activeTab == 'ipsTab')
            {
              $('#zonesTabTitle').trigger('click');
            }
          }
        } else {
          $("#ipsTab").show();
        }
        //Store the Cisco recommended settings
        if ($('#recommmendedSecuritySettingsCheck').is(':checked')) {
          deviceCommunicator.getConfigCmdOutput("service password-encryption");
        } else {
          deviceCommunicator.getConfigCmdOutput("no service password-encryption");
        }
      }else{
        worker.terminate();
      }
    }
  });

  $("#googleAnalytics").dialog({
    autoOpen: false,
    height: 490,
    width: 675,
    modal: true,
    buttons: [{
        text: $.i18n.prop("yes"),
        click: function() {
      $('#analyticsCheck').prop('checked',true);
          getGATrackCode();
          $(this).dialog("close");
        }}, {
        text: $.i18n.prop("no"),
        click: function() {
      $('#analyticsCheck').prop('checked',false);
          $(this).dialog("close");
        }
      }],
    close: function() {
      var json=getChangedPreferences(true);
      storePreferences(json);
      if (ipsTabHide) {
        $("#ipsTab").hide();
      } else {
        $("#ipsTab").show();
      }
    }
  });
  if (preferences.analytics) {
    getGATrackCode();
  }

  if (oneTimeUsers.length > 0) {
    //loadjscssfile("../external/jQueryFramework.js", "js");
    loadjscssfile("../js/ccpExpressValidation.js", "js");

    $("#oneTimeUSer-dialogForm").dialog({
      autoOpen: false,
      modal: true,
      height: 330,
      width: 550,
      buttons: [{
          text: $.i18n.prop("ok"),
          click: function() {
            if ($('#oneTimeUserForm').valid()) {
              $("#oneTimeUSer-dialogForm").dialog("close");
              setTimeout(function() {
                var arr, response, editUsername;
                arr = $('#oneTimeUserForm').formToArray();
                try {

                  if (oneTimeUsers[NonOneTimeUsers].encrypt === true) {
                    response = deviceCommunicator.configureCommandsFromTemplate("userSecretCreate.txt", arr, false);
                  } else {
                    response = deviceCommunicator.configureCommandsFromTemplate("userPasswordCreate.txt", arr, false);
                  }
                  arr = [];
                  editUsername = oneTimeUsers[NonOneTimeUsers].userName;
                  arr.push({name: "username", value: editUsername});
                  response = deviceCommunicator.configureCommandsFromTemplate("userFormDelete.txt", arr, false);
                  NonOneTimeUsers = NonOneTimeUsers + 1;
                  if (NonOneTimeUsers < oneTimeUsers.length) {
                    $('#oneTimeUserInfo').remove();
                    $('#oneTimeUSer-dialogForm').empty();
                    showOneTimeUser(NonOneTimeUsers, oneTimeUsers);
                  } else {

                    deviceCommunicator.doWriteMemory();
                  }
                } catch (error) {
                  $('#oneTimeUserErrorMessage').html(error.errorResponse);
                  $('#oneTimeUserError').show();
                  $("#oneTimeUSer-dialogForm").dialog("open");
                  return false;
                }
              }, 100);
            }
          }
        }],
      close: function() {
        $("#oneTimeUSer-dialogForm").dialog("close");
      }

    });
    showOneTimeUser(0, oneTimeUsers);
    $('#oneTimeUserInput').keyup(function() {
      var newUserName = $(this).val().toLowerCase();
      newUserName = newUserName.trim("");
      $.validator.addClassRules({
        changeUser: {changeUsername: true}
      });
      $.validator.addMethod("changeUsername", function(value, element) {
        return (!(newUserName === oneTimeUsers[NonOneTimeUsers].userName));
      }, "Please change username");

    }).keyup();

    validatorUser = $('#oneTimeUserForm').validate({
      errorElement: "div",
      wrapper: "div",
      errorPlacement: function(error, element) {
        error.insertAfter(element.parent());
      }
    });


  }

  /**
   * Animations for landing page start.
   * The variable needLandingPageAnimation should be true for the animations to enable.
   */

  /**
   * The class fa-spin should be changed to fa-pulse when font awesome 4.3.0 or higher is incorporated.
   */
  var animClassName = 'fa-pulse';
  $("#topnav-7").hover(
    function() {
      if (needLandingPageAnimation) {
        $(this).find("em").addClass(animClassName);
      }
    },
    function() {
      if (needLandingPageAnimation) {
        $(this).find("em").removeClass(animClassName);
      }
    }
  );

  /*
   $("#topnav-8").mouseover(function() {
   if (needLandingPageAnimation) {
   $(this).find("em").addClass('fa-spin');
   }
   }).mouseout(function() {
   if (needLandingPageAnimation) {
   $(this).find("em").removeClass('fa-spin');
   }
   });
   */

   /*
  var anycliFAClass = $("#topnav-8").find("em");
  var anycliFAIconAnim = false, anycliFAIAnimationRunning = false;
  $("#topnav-8").hover(
    function() {
      if (needLandingPageAnimation) {
        if (anycliFAIconAnim === false)
        {
          anycliFAIAnimationRunning = true;

          anycliFAClass.css('font-size', '20px');
          anycliFAClass.css('padding-top', '28px');
          anycliFAIconAnim =
            setInterval(function() {
              if (anycliFAIAnimationRunning)
              {
                anycliFAClass.css('font-size', '48px');
                anycliFAClass.css('padding-top', '0px');
              }
              setTimeout(function() {
                if (anycliFAIAnimationRunning)
                {
                  anycliFAClass.css('font-size', '20px');
                  anycliFAClass.css('padding-top', '28px');
                }
              }, 300)
            }, 600
              );
        }
      }
    },
    function() {
      if (needLandingPageAnimation) {
        clearInterval(anycliFAIconAnim);
        anycliFAIconAnim = false;
        anycliFAIAnimationRunning = false;
        setTimeout(function() {
          anycliFAClass.css('font-size', '48px');
          anycliFAClass.css('padding-top', '0px');
        }, 100);

      }
    }
  );
*/

  /**
   * The above animation for topnav-8 was replaced by below icon animation after the ICON is changed to fa-terminal
   */


   var anycliFAClass = $("#topnav-8").find("em");
   var anycliFAIconAnim = false, anycliFAIAnimationRunning = false;
   $("#topnav-8").hover(
   function() {
   if (needLandingPageAnimation &&
       anycliFAIconAnim === false)
   {
   anycliFAIAnimationRunning = true;
   //anycliFAClass.toggleClass('fa-angle-right fa-terminal');
   anycliFAIconAnim =
   setInterval(function(){
   ////consoleLog(Date()+"started toggling");
   if (anycliFAIAnimationRunning) {
   anycliFAClass.toggleClass('fa-angle-right fa-terminal');
   }

   setTimeout(function(){

   if (anycliFAIAnimationRunning) {
   anycliFAClass.toggleClass('fa-angle-right fa-terminal');
   }
   ////consoleLog(Date()+"just toggling");
   },300)
   },600
   );

   }
   },
   function() {
   if (needLandingPageAnimation) {
   clearInterval(anycliFAIconAnim);
   anycliFAIconAnim = false;
   anycliFAIAnimationRunning = false;
   setTimeout(function(){
   if (anycliFAClass.hasClass('fa-angle-right')) {
   ////consoleLog(anycliFAClass.parent().html());
   anycliFAClass.toggleClass('fa-angle-right fa-terminal');
   ////consoleLog(anycliFAClass.parent().html());
   ////consoleLog("toggling final");
   }
   },100);
   }
   }
   );


  var stRouteFAClass = $("#topnav-4").find("em");
  var stRouteFAIconAnim = false, stRouteFAIAnimationRunning = false;
  $("#topnav-4").hover(
    function() {
      if (needLandingPageAnimation &&
          stRouteFAIconAnim === false)
        {
          stRouteFAIAnimationRunning = true;
          stRouteFAClass.addClass('fa-flip-vertical');
          stRouteFAIconAnim =
            setInterval(
              function() {
                if (stRouteFAIAnimationRunning)
                {
                  stRouteFAClass.removeClass('fa-flip-vertical');
                }
                setTimeout(function() {
                  if (stRouteFAIAnimationRunning)
                  {
                    stRouteFAClass.addClass('fa-flip-vertical');
                  }
                }, 300)
              }, 600
              );
        }

    },
    function() {
      if (needLandingPageAnimation) {
        clearInterval(stRouteFAIconAnim);
        stRouteFAIconAnim = false;
        stRouteFAIAnimationRunning = false;
        setTimeout(function() {
          if (stRouteFAClass.hasClass('fa-flip-vertical')) {
            ////consoleLog(stRouteFAClass.parent().html());
            stRouteFAClass.removeClass('fa-flip-vertical');
            ////consoleLog(stRouteFAClass.parent().html());
            ////consoleLog("toggling final");
          }
        }, 100);
      }
    }
  );
  
  var aclFAClass = $("#topnav-13").find("em");
  var aclFAIconAnim = false, aclFAIAnimationRunning = false;
  $("#topnav-13").hover(
    function() {
      if (needLandingPageAnimation &&
          aclFAIconAnim === false)
        {
          aclFAIAnimationRunning = true;
          aclFAClass.addClass('fa-unlock');
          aclFAIconAnim =
            setInterval(
              function() {
                if (aclFAIAnimationRunning)
                {
                  aclFAClass.removeClass('fa-unlock');
                }
                setTimeout(function() {
                  if (aclFAIAnimationRunning)
                  {
                    aclFAClass.addClass('fa-unlock');
                  }
                }, 300)
              }, 600
              );
        }

    },
    function() {
      if (needLandingPageAnimation) {
        clearInterval(aclFAIconAnim);
        aclFAIconAnim = false;
        aclFAIAnimationRunning = false;
        setTimeout(function() {
          if (aclFAClass.hasClass('fa-unlock')) {
            ////consoleLog(stRouteFAClass.parent().html());
            aclFAClass.removeClass('fa-unlock');
            ////consoleLog(stRouteFAClass.parent().html());
            ////consoleLog("toggling final");
          }
        }, 100);
      }
    }
  );

  var wizardFAClass = $("#topnav-12").find("em");
  var wizardFAIconAnim = false, wizardFAIAnimationRunning = false;
  $("#topnav-12").hover(
    function() {
      if (needLandingPageAnimation &&
          wizardFAIconAnim === false)
        {
          wizardFAIAnimationRunning = true;
          //wizardFAClass.toggleClass('fa-forward fa-fast-forward');
          wizardFAIconAnim =
            setInterval(function() {
              ////consoleLog(Date()+"started toggling");
              if (wizardFAIAnimationRunning) {
                wizardFAClass.toggleClass('fa-forward fa-fast-forward');
              }

              setTimeout(function() {

                if (wizardFAIAnimationRunning) {
                  wizardFAClass.toggleClass('fa-forward fa-fast-forward');
                }
                ////consoleLog(Date()+"just toggling");
              }, 300)
            }, 600
              );
        }

    },
    function() {
      if (needLandingPageAnimation) {
        clearInterval(wizardFAIconAnim);
        wizardFAIconAnim = false;
        wizardFAIAnimationRunning = false;
        setTimeout(function() {
          if (wizardFAClass.hasClass('fa-forward')) {
            ////consoleLog(wizardFAClass.parent().html());
            wizardFAClass.toggleClass('fa-fast-forward fa-forward');
            ////consoleLog(wizardFAClass.parent().html());
            ////consoleLog(Date()+"toggling final");
          }
        }, 100);
      }
    }
  );


  var caaFAClass = $("#topnav-9").find("em");
  var caaFAIconAnim = false, caaFAIAnimationRunning = false;
  $("#topnav-9").hover(
    function() {
      if (needLandingPageAnimation &&
          caaFAIconAnim === false)
        {
          caaFAIAnimationRunning = true;
          //caaFAClass.toggleClass('fa-cloud fa-cloud-upload');
          caaFAIconAnim =
            setInterval(function() {
              ////consoleLog(Date()+"started toggling");
              if (caaFAIAnimationRunning) {
                caaFAClass.toggleClass('fa-cloud fa-cloud-upload');
              }

              setTimeout(function() {

                if (caaFAIAnimationRunning) {
                  caaFAClass.toggleClass('fa-cloud fa-cloud-upload');
                }
                ////consoleLog(Date()+"just toggling");
              }, 300)
            }, 600
              );
        }

    },
    function() {
      if (needLandingPageAnimation) {
        clearInterval(caaFAIconAnim);
        caaFAIconAnim = false;
        caaFAIAnimationRunning = false;
        setTimeout(function() {
          if (caaFAClass.hasClass('fa-cloud')) {
            ////consoleLog(caaFAClass.parent().html());
            caaFAClass.toggleClass('fa-cloud fa-cloud-upload');
            ////consoleLog(caaFAClass.parent().html());
            ////consoleLog("toggling final");
          }
        }, 100);
      }
    }
  );

  var identityFAClass = $("#topnav-3").find("em");
  var identityFAIconAnim = false, identityFAIAnimationRunning = false;
  $("#topnav-3").hover(
    function() {
      if (needLandingPageAnimation &&
          identityFAIconAnim === false)
        {
          identityFAIAnimationRunning = true;
          identityFAClass.toggleClass('fa-users fa-user-plus');
          identityFAIconAnim =
            setInterval(function() {
              ////consoleLog(Date()+"started toggling");
              if (identityFAIAnimationRunning) {
                identityFAClass.toggleClass('fa-users fa-user-plus');
              }

              setTimeout(function() {

                if (identityFAIAnimationRunning) {
                  identityFAClass.toggleClass('fa-users fa-user-plus');
                }
                ////consoleLog(Date()+"just toggling");
              }, 300)
            }, 600
              );
        }

    },
    function() {
      if (needLandingPageAnimation) {
        clearInterval(identityFAIconAnim);
        identityFAIconAnim = false;
        identityFAIAnimationRunning = false;
        setTimeout(function() {
          if (identityFAClass.hasClass('fa-user-plus')) {
            ////consoleLog(identityFAClass.parent().html());
            identityFAClass.toggleClass('fa-users fa-user-plus');
            ////consoleLog(identityFAClass.parent().html());
            ////consoleLog("toggling final");
          }
        }, 100);
      }
    }
  );

  var dhcpdnsFAClass = $("#topnav-2").find("em");
  var dhcpdnsFAIconAnim = false, dhcpdnsFAIAnimationRunning = false;
  $("#topnav-2").hover(
    function() {
      if (needLandingPageAnimation &&
          dhcpdnsFAIconAnim === false)
        {
          dhcpdnsFAIAnimationRunning = true;
          //dhcpdnsFAClass.toggleClass('fa-folder fa-folder-open');
          dhcpdnsFAIconAnim =
            setInterval(function() {
              ////consoleLog(Date()+"started toggling");
              if (dhcpdnsFAIAnimationRunning) {
                dhcpdnsFAClass.toggleClass('fa-cog fa-cogs');
              }

              setTimeout(function() {

                if (dhcpdnsFAIAnimationRunning) {
                  dhcpdnsFAClass.toggleClass('fa-cog fa-cogs');
                }
                ////consoleLog(Date()+"just toggling");
              }, 300)
            }, 600
              );
        }

    },
    function() {
      if (needLandingPageAnimation) {
        clearInterval(dhcpdnsFAIconAnim);
        dhcpdnsFAIconAnim = false;
        dhcpdnsFAIAnimationRunning = false;
        setTimeout(function() {
          if (dhcpdnsFAClass.hasClass('fa-folder')) {
            ////consoleLog(dhcpdnsFAClass.parent().html());
            dhcpdnsFAClass.toggleClass('fa-folder fa-folder-open');
            ////consoleLog(dhcpdnsFAClass.parent().html());
            ////consoleLog("toggling final");
          }
        }, 100);
      }
    }
  );


  var securityFAClass = $("#topnav-11").find("em");
  var securityFAIconAnim = false, securityFAIAnimationRunning = false;
  $("#topnav-11").hover(
    function() {
      if (needLandingPageAnimation &&
          securityFAIconAnim === false)
        {
          securityFAIAnimationRunning = true;
          //securityFAClass.addClass('fa-flip-horizontal');
          securityFAIconAnim =
            setInterval(function() {
              ////consoleLog(Date()+"started toggling");
              if (securityFAIAnimationRunning) {
                securityFAClass.addClass('fa-flip-horizontal');
              }

              setTimeout(function() {

                if (securityFAIAnimationRunning) {
                  securityFAClass.removeClass('fa-flip-horizontal');
                }
                ////consoleLog(Date()+"just toggling");
              }, 300)
            }, 600
              );
        }

    },
    function() {
      if (needLandingPageAnimation) {
        clearInterval(securityFAIconAnim);
        securityFAIconAnim = false;
        securityFAIAnimationRunning = false;
        setTimeout(function() {
          securityFAClass.removeClass('fa-flip-horizontal');
        }, 100);
      }
    }
  );


  var dashboardFAClass = $("#topnav-5").find("em");
  var dashboardFAIconAnim = false, dashboardFAIAnimationRunning = false;
  $("#topnav-5").hover(
    function() {
      if (needLandingPageAnimation &&
          dashboardFAIconAnim === false)
        {
          dashboardFAIAnimationRunning = true;
          //dashboardFAClass.addClass('fa-flip-horizontal');
          dashboardFAIconAnim =
            setInterval(function() {
              ////consoleLog(Date()+"started toggling");
              if (dashboardFAIAnimationRunning) {
                dashboardFAClass.addClass('fa-flip-horizontal');
              }

              setTimeout(function() {

                if (dashboardFAIAnimationRunning) {
                  dashboardFAClass.removeClass('fa-flip-horizontal');
                }
                ////consoleLog(Date()+"just toggling");
              }, 300)
            }, 600
              );
        }

    },
    function() {
      if (needLandingPageAnimation) {
        clearInterval(dashboardFAIconAnim);
        dashboardFAIconAnim = false;
        dashboardFAIAnimationRunning = false;
        setTimeout(function() {
          dashboardFAClass.removeClass('fa-flip-horizontal');
        }, 100);
      }
    }
  );

  var interfaceFAClass = $("#topnav-1").find("em");
  var interfaceFAIconAnim = false, interfaceFAIAnimationRunning = false;
  $("#topnav-1").hover(
    function() {
      if (needLandingPageAnimation &&
          interfaceFAIconAnim === false)
        {
          interfaceFAIAnimationRunning = true;
          interfaceFAClass.css('color', '#fff');
          interfaceFAIconAnim =
            setInterval(function() {
              ////consoleLog(Date()+"started toggling");
              if (interfaceFAIAnimationRunning) {
                interfaceFAClass.css('color', '#198fc4');
              }

              setTimeout(function() {

                if (interfaceFAIAnimationRunning) {
                  interfaceFAClass.css('color', '#fff');
                }
                ////consoleLog(Date()+"just toggling");
              }, 300)
            }, 600
              );
        }

    },
    function() {
      if (needLandingPageAnimation) {
        clearInterval(interfaceFAIconAnim);
        interfaceFAIconAnim = false;
        interfaceFAIAnimationRunning = false;
        setTimeout(function() {
          interfaceFAClass.css('color', '#5c5c5c');
        }, 100);
      }
    }
  );

/* PnP will be hidden as its EoL. Commenting out the code for PnP Logo Animation */

/*
  var pnpFAClass = $("#topnav-6").find("em");
  var pnpFAIconAnim = false, pnpFAIAnimationRunning = false;
  $("#topnav-6").hover(
    function() {
      if (needLandingPageAnimation &&
          pnpFAIconAnim === false)
        {
          pnpFAIAnimationRunning = true;
          pnpFAClass.css('color', '#fff');
          pnpFAIconAnim =
            setInterval(function() {
              ////consoleLog(Date()+"started toggling");
              if (pnpFAIAnimationRunning) {
                pnpFAClass.css('color', '#198fc4');
              }

              setTimeout(function() {

                if (pnpFAIAnimationRunning) {
                  pnpFAClass.css('color', '#fff');
                }
                ////consoleLog(Date()+"just toggling");
              }, 300)
            }, 600
              );
        }

    },
    function() {
      if (needLandingPageAnimation) {
        clearInterval(pnpFAIconAnim);
        pnpFAIconAnim = false;
        pnpFAIAnimationRunning = false;
        setTimeout(function() {
          pnpFAClass.css('color', '#5c5c5c');
        }, 100);
      }
    }
  );
*/
  var wirelessFAClass = $("#topnav-10").find("em");
  var wirelessFAIconAnim = false, wirelessFAIAnimationRunning = false;
  $("#topnav-10").hover(
    function() {
      if (needLandingPageAnimation &&
          wirelessFAIconAnim === false)
        {
          wirelessFAIAnimationRunning = true;

          wirelessFAClass.css('font-size', '36px');
          wirelessFAClass.css('padding-top', '12px');
          wirelessFAIconAnim =
            setInterval(function() {
              if (wirelessFAIAnimationRunning)
              {
                wirelessFAClass.css('font-size', '48px');
                wirelessFAClass.css('padding-top', '0px');
              }
              setTimeout(function() {
                if (wirelessFAIAnimationRunning)
                {
                  wirelessFAClass.css('font-size', '36px');
                  wirelessFAClass.css('padding-top', '12px');
                }
              }, 300)
            }, 600
              );
        }

    },
    function() {
      if (needLandingPageAnimation) {
        clearInterval(wirelessFAIconAnim);
        wirelessFAIconAnim = false;
        wirelessFAIAnimationRunning = false;
        setTimeout(function() {
          wirelessFAClass.css('font-size', '48px');
          wirelessFAClass.css('padding-top', '0px');
        }, 100);

      }
    }
  );


  var qwizFAClass = $("#basictopnav-12").find("em");
  var qwizFAIconAnim = false, qwizFAIAnimationRunning = false;
  $("#basictopnav-12").hover(
    function() {
      if (needLandingPageAnimation &&
          qwizFAIconAnim === false)
        {
          qwizFAIAnimationRunning = true;
          //qwizFAClass.toggleClass('fa-forward fa-fast-forward');
          qwizFAIconAnim =
            setInterval(function() {
              ////consoleLog(Date()+"started toggling");
              if (qwizFAIAnimationRunning) {
                qwizFAClass.toggleClass('fa-forward fa-fast-forward');
              }

              setTimeout(function() {

                if (qwizFAIAnimationRunning) {
                  qwizFAClass.toggleClass('fa-forward fa-fast-forward');
                }
                ////consoleLog(Date()+"just toggling");
              }, 300)
            }, 600
              );
        }

    },
    function() {
      if (needLandingPageAnimation) {
        clearInterval(qwizFAIconAnim);
        qwizFAIconAnim = false;
        qwizFAIAnimationRunning = false;
        setTimeout(function() {
          if (qwizFAClass.hasClass('fa-forward')) {
            ////consoleLog(qwizFAClass.parent().html());
            qwizFAClass.toggleClass('fa-fast-forward fa-forward');
            ////consoleLog(qwizFAClass.parent().html());
            ////consoleLog(Date()+"toggling final");
          }
        }, 100);
      }
    }
  );

  $('#runningConfigBackup').tooltip({
      tooltipClass: "custom-tooltip-styling"
  });

  var advsetupFAClass = $("#basictopnav-13").find("em");
  var advsetupFAIconAnim = false, advsetupFAIAnimationRunning = false;
  $("#basictopnav-13").hover(
    function() {
      if (needLandingPageAnimation &&
          advsetupFAIconAnim === false)
        {
          advsetupFAIAnimationRunning = true;
          //advsetupFAClass.toggleClass('fa-align-justify fa-list');
          advsetupFAIconAnim =
            setInterval(function() {
              ////consoleLog(Date()+"started toggling");
              if (advsetupFAIAnimationRunning) {
                advsetupFAClass.toggleClass('fa-align-justify fa-list');
              }

              setTimeout(function() {

                if (advsetupFAIAnimationRunning) {
                  advsetupFAClass.toggleClass('fa-align-justify fa-list');
                }
                ////consoleLog(Date()+"just toggling");
              }, 300)
            }, 600
              );
        }

    },
    function() {
      if (needLandingPageAnimation) {
        clearInterval(advsetupFAIconAnim);
        advsetupFAIconAnim = false;
        advsetupFAIAnimationRunning = false;
        setTimeout(function() {
          if (advsetupFAClass.hasClass('fa-align-justify')) {
            ////consoleLog(advsetupFAClass.parent().html());
            advsetupFAClass.toggleClass('fa-align-justify fa-list');
            ////consoleLog(advsetupFAClass.parent().html());
            ////consoleLog(Date()+"toggling final");
          }
        }, 100);
      }
    }
  );
});

function getFormattedDate() {
        var date = new Date();
        var str = date.getFullYear() + "-" + (date.getMonth() + 1) + "-" + date.getDate() + " " +  date.getHours() + ":" + date.getMinutes() + ":" + date.getSeconds();

        return str;
}

function getHostName(){	
	var hostnameString = deviceCommunicator.getExecCmdOutput("show run | i hostname");
	var hostnameSplit = hostnameString.split(" ");
	var hostname = hostnameSplit[1];
	return hostname;	
}

function getHostIPAddress(){
	var ipAddress = $(location).attr('hostname');
	return ipAddress;
}
function createConfig(configData,fileName,ext){
        // download stuff
            $('#tempDownload').remove();
            var buffer = configData;
			var ipaddress = getHostIPAddress();
			var hostname = getHostName();
			if (hostname !== null || hostname !== undefined || hostname !== ""){
               fileName=fileName+"_"+getFormattedDate()+"_"+hostname+ext;
			}
			else{
			   fileName=fileName+"_"+getFormattedDate()+"_"+ipaddress+ext;
			}
            var blob = new Blob([buffer], {
                "type": "text/plain;charset=utf8;"
            });
            var link = document.createElement("a");
                        // feature detection
            if(link.download !== undefined) {
                // Browsers that support HTML5 download attribute
                link.setAttribute("href", window.URL.createObjectURL(blob));
                link.setAttribute("download", fileName);
            }
            else if(navigator.msSaveBlob) {
                                // IE 10+
                navigator.msSaveBlob(blob, fileName);
            } else {
                // it needs to implement server side export
                //alert($.i18n.prop("dlnotsupbrow"));
            }
            link.innerHTML = "Export";
            link.style.display='none';
                        link.setAttribute("id", "tempDownload");
            document.body.appendChild(link);
                        link.click();
}

function getRunningConfigOutput()
{
  if (!shRunConfigLatest || shRunConfigOutput == null || shRunConfigOutput =="") {
    shRunConfigOutput = deviceCommunicator.getExecCmdOutput("show running-config");
    shRunConfigLatest = true;
  }
  var runConfOutput = shRunConfigOutput;
  return runConfOutput;
}

function isDmvpnSpokeEnabledForDevice(liceUid) {
  //consoleLogMethodDetailsStart("performChecks.js", "isDmvpnSpokeEnabledForDevice()");
  var found = true, licenseSplit;
  try {
    resp = liceUid;
    licenseSplit = resp.split("\n");
    for (var i = 1; i < licenseSplit.length; i++) {
      var licenseDetails = licenseSplit[i].split(/\s+/);
      if (licenseDetails[1] != undefined && licenseDetails[1].trim() == "C841M-4X-JSEC/K9") 
      {
        found = false;
        break;
      }
    }
    //consoleLogMethodDetailsEnd("performChecks.js", "isDmvpnSpokeEnabledForDevice()");
    return found;
  } catch (error) {
    errorLogInConsole("Error in isDmvpnSpokeEnabledForDevice()");
    //consoleLogMethodDetailsEndWithError("performChecks.js", "isDmvpnSpokeEnabledForDevice()",error);
    return found;
  }
}

function isDmvpnHubEnabledForDevice(liceUid) {
  //consoleLogMethodDetailsStart("performChecks.js", "isDmvpnHubEnabledForDevice()");
  var found = true, licenseSplit;
  try {
    resp = liceUid;
    licenseSplit = resp.split("\n");
    for (var i = 1; i < licenseSplit.length; i++) {
      var licenseDetails = licenseSplit[i].split(/\s+/);
      //console.log("Box type is ------->>>"+licenseDetails[1].trim()+"<<<------");
      if (licenseDetails[1] != undefined && licenseDetails[1].trim() == "C841M-4X-JSEC/K9") 
      {
        found = false;
        break;
      }
    }
    //consoleLogMethodDetailsEnd("performChecks.js", "isDmvpnHubEnabledForDevice()");
  } catch (error) {
    errorLogInConsole("Error in isDmvpnHubEnabledForDevice()" + error);
    //consoleLogMethodDetailsEndWithError("performChecks.js", "isDmvpnHubEnabledForDevice()",error);
 }
    return found;
}

function badBrowser() {
  //consoleLogMethodDetailsStart("performChecks.js", "badBrowser()");
  
  //$.browser.chrome = /chrome/.test(navigator.userAgent.toLowerCase());
  var userAgent = navigator.userAgent.toLowerCase();
  // IE 11 check
  var isIE11 = !!userAgent.match(/trident.*rv\:11\./);
  
  if(userAgent.indexOf('chrome') != -1 && userAgent.indexOf('safari') != -1 && userAgent.indexOf('edge') != -1) { 
    userAgent = userAgent.substring(userAgent.indexOf('edge/') + 5);
    userAgent = userAgent.substring(0,userAgent.indexOf('.'));
	browserVersion = userAgent;
    browserName = "Edge"; 
  } else if (userAgent.indexOf('msie') != -1) {
    userAgent = userAgent.substring(userAgent.indexOf('msie') + 5);
    userAgent = userAgent.substring(0,userAgent.indexOf('.'));	
    browserVersion = userAgent;
    browserName = "Internet Explorer";
  } else if (isIE11) {
    userAgent = userAgent.substring(userAgent.indexOf('rv') + 3);
    userAgent = userAgent.substring(0,userAgent.indexOf('.'));	
    browserVersion = userAgent;
    browserName = "Internet Explorer";
  } else if (userAgent.indexOf('chrome') == -1 && userAgent.indexOf('safari') != -1 && userAgent.indexOf('opr') == -1) {    
    userAgent = userAgent.substring(userAgent.indexOf('safari/') + 8);
    userAgent = userAgent.substring(0, userAgent.indexOf('.'));
    browserVersion = userAgent;
    browserName = "Safari";         
  } else if (userAgent.indexOf('chrome') != -1  && userAgent.indexOf('safari') != -1 && userAgent.indexOf('opr') == -1) {
    userAgent = userAgent.substring(userAgent.indexOf('chrome/') + 7);
    userAgent = userAgent.substring(0, userAgent.indexOf('.'));
    browserVersion = userAgent;
    $.browser.safari = false;
    browserName = "Chrome";
  } else if (userAgent.indexOf('chrome') != -1 && userAgent.indexOf('safari') != -1 && userAgent.indexOf('opr') != -1) {
	userAgent = userAgent.substring(userAgent.indexOf('opr/') + 4);
	userAgent = userAgent.substring(0,userAgent.indexOf('.'));
	browserVersion = userAgent;
	browserName = "Opera";
  } else if (userAgent.indexOf('firefox') != -1) {    
    userAgent = userAgent.substring(userAgent.indexOf('firefox/') + 8);
    userAgent = userAgent.substring(0, userAgent.indexOf('.'));
    browserVersion = userAgent;
    browserName = "Firefox";         
  }
  
  /*
  if ($.browser.chrome) {
    userAgent = userAgent.substring(userAgent.indexOf('chrome/') + 7);
    userAgent = userAgent.substring(0, userAgent.indexOf('.'));
    version = userAgent;
  } else if ($.browser.mozilla) {
    userAgent = userAgent.substring(userAgent.indexOf('firefox/') + 8);
    userAgent = userAgent.substring(0, userAgent.indexOf('.'));
    version = userAgent;
  } else if ($.browser.msie) {
    version = parseInt($.browser.version, 10);
  }*/
  //consoleLogMethodDetailsEnd("performChecks.js", "badBrowser()");
  if (!((browserName == "Chrome" && browserVersion >= 30) || (browserName == "Firefox" && browserVersion >= 25) ||(browserName == "Internet Explorer" && browserVersion >=10))) { 
    return true; 
  }
  return false;
}
function getBadBrowser(c_name)
{
  //consoleLogMethodDetailsStart("performChecks.js", "getBadBrowser()");
  if (document.cookie.length > 0)
  {
    c_start = document.cookie.indexOf(c_name + "=");
    if (c_start != -1)
    {
      c_start = c_start + c_name.length + 1;
      c_end = document.cookie.indexOf(";", c_start);
      if (c_end == -1){
        c_end = document.cookie.length;}
      //consoleLogMethodDetailsEnd("performChecks.js", "getBadBrowser()");
      return unescape(document.cookie.substring(c_start, c_end));
    }
  }
  //consoleLogMethodDetailsEnd("performChecks.js", "getBadBrowser()");
  return "";
}

function setBadBrowser(c_name, value)
{
  document.cookie = c_name + "=" + escape(value);
}
if (badBrowser() && getBadBrowser('browserWarning') != 'seen') {
  $(function() {
    $('.expand-down ul').append('<div  id="browserInfoVer" class="browserInfo"></div>');
    $('#browserInfoVer').append('<p><img src="images/information.png"/><span id="browserInfoVerClose" class="browserInfoClose"></span><span id="browserInfoVerMessage" class="browserInfoMessage"><noscript id="scriptDisable">' + $.i18n.prop("ScriptMessage") + '</noscript></span></p>');
    $('#browserInfoVerMessage').html($.i18n.prop("browserVersion"));
    $('#browserInfoVerClose').html("<a href='#'  id='warningClose'><span class='closeButton' title='" + $.i18n.prop("closeInfoWindow") + "'></span></a>");
    $('#browserInfoVer').show();
    if ($.browser.msie) {
      $('#browserInfoVerClose').css({position: 'absolute', top: 0, left: 487});
    }
    $('#warningClose').click(function() {
      setBadBrowser('browserWarning', 'seen');

      $('#browserInfoVer').hide();
      return false;
    });
  });
}
function versionAlertBox() {
  //consoleLogMethodDetailsStart("performChecks.js", "versionAlertBox()");

  $(function() {
    $('.expand-down ul').append('<div id="iosInfo"  class="browserInfo"></div>');
    $('#iosInfo').append('<p><img src="images/information.png"/><span id="iosInfoClose" class="browserInfoClose"></span><span id="iosInfoMessage" class="browserInfoMessage"><noscript id="scriptDisable">' + $.i18n.prop("ScriptMessage") + ' </noscript></span></p>');
    $('#iosInfoMessage').html($.i18n.prop("routerIOS"));
    $('#iosInfoClose').html("<a href='#'  id='iosClose'><span class='closeButton' title='" + $.i18n.prop("closeInfoWindow") + "'></span></a>");
    $('#iosInfo').show();
    if ($.browser.msie) {
      $('#iosInfoClose').css({position: 'absolute', top: 0, left: 487});
    }
    //consoleLogMethodDetailsEnd("performChecks.js", "versionAlertBox()");
    $('#iosClose').click(function() {

      $('#iosInfo').hide();
      return false;
    });
  });
}
