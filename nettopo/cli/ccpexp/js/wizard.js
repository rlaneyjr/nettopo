// JavaScript Document
var basicFormArray = [], primaryFormArray = [], backupFormArray = [],lanFormArray=[], securityFormArray = [], mergedCli = "", formatedEM = "", redirectInterval,lanCli="";
function arrayToJson(inArray, nameofObject) {
  //consoleLogMethodDetailsStart("wizard.js", "arrayToJson()");
  //var myJsonString;
  var temArray = {};
  var mainArray = {};
  for (var countArray = 0; countArray < inArray.length; countArray++) {
    elemname = inArray[countArray].name;
    elemvalue = inArray[countArray].value;
    if ((elemvalue.toLowerCase() != "none") && (elemvalue.toLowerCase() != "")) {
      //code
      if (elemname == "wizardbasictimezone") {
        //code
        elemvalue = elemvalue.replace(".", " ");
      }
      temArray[elemname] = elemvalue;
    }

  }
  mainArray[nameofObject] = temArray;
  //consoleLogMethodDetailsEnd("wizard.js", "arrayToJson()");
  return JSON.parse(JSON.stringify(mainArray));
}

/*type-> success/fail */
function createToast(type, message, icon, timeout) {
  //consoleLogMethodDetailsStart("wizard.js", "createToast()");
  $('.wizardToast').remove();
  $('body').append('<div class="wizardToast"><div class="notify-icon"></div><div class="wizardToastMsg">'+
                   '<div class="headerMsg ccpexpCSSReplaceClass884" ></div>'+
                   '<div class="wizardToastText ccpexpCSSReplaceClass885" ></div></div></div>');
  $(".notify-icon").append('<em class="fa ' + icon + '"></em>');
  $(".wizardToastText").text(message);

  if (type == "success") {
    if ($('.wizardToast').hasClass('wizardToastFail')) {
      $('.wizardToast').remove('wizardToastFail');
    }
    $('.wizardToast').addClass('wizardToastSuccess');
    $('.headerMsg').text($.i18n.prop("toastSuccess"));
  }
  else if (type == "fail") {
    if ($('.wizardToast').hasClass('wizardToastSuccess')) {
      $('.wizardToast').remove('wizardToastSuccess');
    }
    $('.wizardToast').addClass('wizardToastFail');
    $('.headerMsg').text($.i18n.prop("toastFailed"));
  }
  $(".wizardToast").animate({bottom: "20px"});
  setTimeout(function() {
    $(".wizardToast").fadeOut("fast", function() {
      $(".wizardToast").css("bottom", "-200px");
    });
  }, timeout)
  //consoleLogMethodDetailsEnd("wizard.js", "createToast()");
}

function previewCli() {
  //consoleLogMethodDetailsStart("wizard.js", "previewCli()");
   $('.previewWindow').animate({scrollTop:0}, 100);
  _.templateSettings.interpolate = /\{\{(.+?)\}\}/g;
  var CLIValue = "", EMScript = "";
  var templateName = "Quick_Setup.txt";
  CLIValue = getTemplateContent(templateName);
  EMScript = getTemplateContent("EMScriptTemplate.txt");
  var jsonArg = arrayToJson(basicFormArray, "basicForm");
  var jsonArg2 = arrayToJson(primaryFormArray, "primaryForm");
  var jsonArg3 = arrayToJson(backupFormArray, "backupwanform");
  var jsonArg4 = arrayToJson(securityFormArray, "securityForm");
  var jsonArg5 =arrayToJson(lanFormArray,"lanForm");
  //consoleLog($.concat(jsonArg, jsonArg2, jsonArg3, jsonArg4));
  var cliTemp = _.template(CLIValue, $.concat(jsonArg, jsonArg2, jsonArg3, jsonArg4,jsonArg5));
  var emTemp = _.template(EMScript, $.concat(jsonArg, jsonArg2, jsonArg3, jsonArg4,jsonArg5));
  formatedEM = formatCli(emTemp);
  mergedCli = formatCli(cliTemp);
  lanCli=configureWizard.checkChangeNetwork();
  $("#clipreview").text(mergedCli + "\n" + formatedEM+"\n"+lanCli);
  //consoleLogMethodDetailsEnd("wizard.js", "previewCli()");
}

function formatCli(cli) {
  //consoleLogMethodDetailsStart("wizard.js", "formatCli()");
  var cliLine = cli.split("\n");
  var find = 'BREAK;';
  var re = new RegExp(find, 'g');
  var tempArr = [];
  var tempText = "";
  $.each(cliLine, function(index, value) {
    tempText = value.trim();
    if (tempText != "") {
      tempArr.push(tempText);
    }
    tempText = "";
  });
  var tempString = tempArr.join('\n');
  //consoleLogMethodDetailsEnd("wizard.js", "formatCli()");
  return tempString.replace(re, "\n");
}
function getTemplateContent(templateName) {
  //consoleLogMethodDetailsStart("wizard.js", "getTemplateContent()");
  //code
  //var templateName="Quick_Setup.txt";
  var CLIValue = "";
  $.ajaxSetup({async: false});
  $.get("../templates2\/" + templateName,
    function(data) {
      CLIValue = data;
      //alert("data"+data);
    }, "text"
    );
  $.ajaxSetup({async: true});
  //consoleLogMethodDetailsEnd("wizard.js", "getTemplateContent()");
  return CLIValue;
}
function wizardformElementHide(hideAndShowArry_Elem) {
  //consoleLogMethodDetailsStart("wizard.js", "wizardformElementHide()");
  //code
  for (var elementCount = 0; elementCount <= hideAndShowArry_Elem.length; elementCount++) {
    $(hideAndShowArry_Elem[elementCount]).hide();
  }
  //consoleLogMethodDetailsEnd("wizard.js", "wizardformElementHide()");
}
function wizardformElementShow(hideAndShowArry_Elem) {
  //consoleLogMethodDetailsStart("wizard.js", "wizardformElementShow()");
  //code
  for (var elementCount = 0; elementCount <= hideAndShowArry_Elem.length; elementCount++) {
    $(hideAndShowArry_Elem[elementCount]).show();
  }
  //consoleLogMethodDetailsEnd("wizard.js", "wizardformElementShow()");
}
function getUrlVariables() {
  //consoleLogMethodDetailsStart("wizard.js", "getUrlVariables()");
  var vars = [], hash, hashes, i;
  hashes = window.location.href.slice(window.location.href.indexOf('?') + 1).split('&');
  for (i = 0; i < hashes.length; i = i + 1) {
    hash = hashes[i].split('=');
    vars.push(hash[0]);
    vars[hash[0]] = hash[1];
  }
  //consoleLogMethodDetailsEnd("wizard.js", "getUrlVariables()");
  return vars;
}
//To get languageName


function openGoogleAnalyticsDialog() {
  //consoleLogMethodDetailsStart("wizard.js", "openGoogleAnalyticsDialog()");
  if (checkCookie() == 'true') {
    getGATrackCode();
  }
  //consoleLogMethodDetailsEnd("wizard.js", "openGoogleAnalyticsDialog()");

}

function enableDisableDashboard() {
  //consoleLogMethodDetailsStart("wizard.js", "enableDisableDashboard()");
  if (!licenseCheck) {
    $("#securityDashboard").hide();
  }
  else {
    $("#securityDashboard").show();
  }
  //consoleLogMethodDetailsEnd("wizard.js", "enableDisableDashboard()");
}

function checkCookie() {
  //consoleLogMethodDetailsStart("wizard.js", "checkCookie()");
  if (GetCookie(name) == null || GetCookie(name) == "undefined") {
    if (isCookiesEnabled()) {
      $("#googleAnalyticsPopUp").dialog("open");
    }
    //consoleLogMethodDetailsEnd("wizard.js", "checkCookie()");
    return 'false';
  }
  else {
    //consoleLogMethodDetailsEnd("wizard.js", "checkCookie()");
    return GetCookie(name);
  }

}
function loadWizardPage() {
  //consoleLogMethodDetailsStart("wizard.js", "loadWizardPage()");
  var first = getUrlVariables()["feature"];
  switch (first) {
    case 'Wizard':

      //$('#content').html(data);
      $('#hideAll').css('display', 'block');
      configureWizard.configureWizardLoading();
      //$.unblockUI();
      //$('ul#bottomnav li#bottomnav-1 a').addClass('toggleopacity');
      //$('#hideAll').css('display','none');
      //setTimeout(openGoogleAnalyticsDialog(),3000);


      break;
  }
  //consoleLogMethodDetailsEnd("wizard.js", "loadWizardPage()");
}
/*function checkSecurityLicense() {
 var found=false;
 resp = deviceCommunicator.getExecCmdOutput("show license feature");
 licenseSplit=resp.split("\n");
 for(var i=1;i<licenseSplit.length;i++){
 var licenseDetails=licenseSplit[i].split(/\s+/);
 if ((licenseDetails[0].trim()=="securityk9" && licenseDetails[4].trim().toLowerCase()=="yes") || (licenseDetails[0].trim()=="advipservices" && licenseDetails[4].trim().toLowerCase()=="yes") || (licenseDetails[0].trim()=="advsecurity")) {
 found=true;
 break;
 }
 }
 try{
 xml = deviceCommunicator.getExecCmdOutput("sh ver | format " + deviceCommunicator.getInstallDir() + "/odm/overviewshVer.odm");
 version = $(xml).find('Version').text();
 ver = parseFloat(version);
 iosVer = ver.toFixed(1);
 if (found && iosVer > 15.3)
 return true;
 else
 return false;
 }
 catch(e){
 //consoleLog(e);
 }

 }*/



/***********************To do Internationalization***********************************/


function loadDashboard() {
  //consoleLogMethodDetailsStart("wizard.js", "loadDashboard()");
  window.location.replace(window.location.href.split("wizard.html")[0] + "frames.html?feature=routerdiagonstics");
  //consoleLogMethodDetailsEnd("wizard.js", "loadDashboard()");
}

function blockPage(msg) {
  //consoleLogMethodDetailsStart("wizard.js", "blockPage()");
  $.blockUI({
    css: {
      border: 'none',
      backgroundColor: 'none'
    },
    message: '<div class="loading_container"><div class="loading_ring loading_blue"></div><div id="loading_content"><span>' + $.i18n.prop(msg) + '</span></div></div>'
  });
  //consoleLogMethodDetailsEnd("wizard.js", "blockPage()");
}

function wizardComponent() {
  //consoleLogMethodDetailsStart("wizard.js", "wizardComponent()");
  /*Wizard code starts here*/
  //fieldsets
  var current_fs, next_fs, previous_fs;
  //fieldset properties which we will animate
  //var left, opacity, scale;
  //flag to prevent quick multi-click glitches
  var animating;
  var wizardSectionValue = "";
  var wizardCheckFlag = false;
  if (!licenseCheck) {

    if (iosk9check == "SecurityEnable") {
      $('#progressbar li').css({"width": "16.5%"});
      $('.dynamicli').show();
      $('.dynamicpropsetting').removeClass("dynamicfieldSet");

    } else {
      $('.dynamicli').hide();
      $('.dynamicpropsetting').addClass("dynamicfieldSet");
      $('#progressbar li').css({"width": "19%"});
    }
  } else {
    $('.dynamicli').show();
    $('.dynamicpropsetting').removeClass("dynamicfieldSet");
    $('#progressbar li').css({"width": "16.5%"});
  }

//$("#welcome").niceScroll({touchbehavior:false,cursorcolor:"rgb(146, 195, 208)",cursoropacitymax:1,cursorwidth:7,cursorborder:"1px solid rgb(142, 160, 229)",cursorborderradius:"8px",background:"rgb(230, 228, 228)",autohidemode:false}); // MAC like scrollbar
//$("#welcome").niceScroll({touchbehavior:false,cursorcolor:"rgb(146, 195, 208)",cursoropacitymax:1,cursorwidth:7,cursorborder:"1px solid rgb(142, 160, 229)",cursorborderradius:"8px",background:"rgb(230, 228, 228)",autohidemode:false}); // MAC like scrollbar
//$("#welcome").niceScroll({touchbehavior:false,cursorcolor: "rgb(146, 195, 208)",cursoropacitymax:1,cursorwidth:6,background:"rgb(230, 228, 228)",autohidemode:false});
  $(".next").click(function() {
    //$("#welcome").niceScroll({touchbehavior:false,cursorcolor:"rgb(146, 195, 208)",cursoropacitymax:1,cursorwidth:7,cursorborder:"1px solid rgb(142, 160, 229)",cursorborderradius:"8px",background:"rgb(230, 228, 228)",autohidemode:false}); // MAC like scrollbar
    wizardSectionValue = $(this).attr("sectionvalue");
    wizardCheckFlag = true;

    if (wizardSectionValue.toLowerCase() == "basicform") {
      basicFormArray = configureWizard.basicformProcessing();
      if (basicFormArray.length > 0) {
        //code
        wizardCheckFlag = true;
      } else {
        wizardCheckFlag = false;
      }
    } else if (wizardSectionValue.toLowerCase() == "primarywanform") {
      primaryFormArray = configureWizard.primaryformProcessing();
      if (primaryFormArray.length > 0) {
        //code
        wizardCheckFlag = true;
        configureWizard.addRemoveInterface();
      } else {
        wizardCheckFlag = false;
      }
    } else if (wizardSectionValue.toLowerCase() == "backupwanform") {

      backupFormArray = configureWizard.backupformProcessing();
      if (backupFormArray.length > 0) {
        //code
        wizardCheckFlag = true;
      } else {
        wizardCheckFlag = false;
      }
    }else if (wizardSectionValue.toLowerCase() == "lanform") {
      lanFormArray = configureWizard.lanformProcessing();
      if (lanFormArray.length > 0) {
        wizardCheckFlag = true;
      } else {
        wizardCheckFlag = false;
      }
    }
    else if (wizardSectionValue.toLowerCase() == "securityform") {
      configureWizard.setConfiguredFeatures();
      securityFormArray = configureWizard.securityformProcessing();
      wizardCheckFlag = true;
    }
    if (wizardCheckFlag) {
      current_fs = $(this).parent().parent();
      next_fs = $(this).parent().parent().next();
      if ($(this).parent().parent().next().hasClass("dynamicfieldSet")) {
        if (wizardSectionValue.toLowerCase() == "lanform") {
          configureWizard.setConfiguredFeatures();

        }
        next_fs = next_fs.next();
      }
      $("#progressbar li").eq(next_fs.attr("showcountnext")).addClass("active").find('a').addClass('btn-2 btn-2i');
      $("#progressbar li").eq(current_fs.attr("showcountnext")).find('a').removeClass('btn-2 btn-2i');
      //show the next fieldset
      current_fs.hide();
      next_fs.show();
    }
    //hide the current fieldset with style

  });
  $(".a_demo_four").click(function() {
    $(".a_demo_four").hide();
    $(".wizardStepsMainDiv").removeClass("minHeight499");
    $(".welcomescreen").slideUp(1000, function() {
      $("#mainwizard").show(500);
      setTimeout(function(){$("#mainwizard").css("min-height","499px")},1000);
    });
  });
  $(".previous").click(function() {
    //$("#welcome").niceScroll({touchbehavior:false,cursorcolor:"rgb(146, 195, 208)",cursoropacitymax:1,cursorwidth:7,cursorborder:"1px solid rgb(142, 160, 229)",cursorborderradius:"8px",background:"rgb(230, 228, 228)",autohidemode:false}); // MAC like scrollbar
    animating = false;

    current_fs = $(this).parent().parent();
    previous_fs = $(this).parent().parent().prev();

    if ($(this).parent().parent().prev().hasClass("dynamicfieldSet")) {
      //code
      previous_fs = previous_fs.prev();
    }
    //de-activate current step on progressbar

    $("#progressbar li").eq(current_fs.attr("showcountnext")).removeClass("active").find('a').removeClass('btn-2 btn-2i');
    $("#progressbar li").eq(previous_fs.attr("showcountnext")).find('a').addClass('btn-2 btn-2i');

    //show the previous fieldset
    current_fs.hide();
    previous_fs.show();
    //hide the current fieldset with style

  });

  $(".submit").click(function() {
    $("#wizardAlertSubmit").dialog("open");
    return false;
  });
  $("#wizardAlertSubmit").dialog({
    autoOpen: false,
    height: 200,
    width: 400,
    modal: true,
    buttons: [{
        text: $.i18n.prop("yesStr"),
        click: function() {
          previewCli();
          blockPage("applyingStr");
          setTimeout(function() {
            try {
              if (isNano){
                configureWizard.profileCreation();
              }
                //only for Cellulr Nano
              if (!isNano && ($('#interfaceSelection').val().toLowerCase().indexOf('cellular') > -1 || ($('#enableBackupWAN').is(':checked') && $('#interfaceBackup').val().toLowerCase().indexOf('cellular') > -1))) {
                configureWizard.createProfileISR();
                //only for Cellulr ISR
              }
            }
            catch (e) {
              errorLogInConsole(e);
            }
            try {
              response = deviceCommunicator.getConfigCmdOutput(mergedCli);
              if (formatedEM.trim() != "") {
                response = deviceCommunicator.getConfigCmdOutput(formatedEM);
              }
              if (isNano){
                configureWizard.activateSim();
              }
              //only for Cellulr Nano

              //deviceCommunicator.doWriteMemory();

        if (lanCli!=="") {
    try{
    deviceCommunicator.getConfigCmdOutput(lanCli,true);
    }
    catch(e){
        errorLogInConsole(e);
    }
    $('.wizardStepsMainDiv').hide();
    $("#msgDiv").show();
    $('.ccpexpCSSReplaceClass325').hide();
    $('.finishButtons').hide();
    $.unblockUI();
        }
        else{
    $.unblockUI();
    $('.lanChangedMsg').hide();
    $('.wizardStepsMainDiv').hide();
    $("#msgDiv").show();
    var count = 30;
    redirectInterval = setInterval(function() {
      if (count > 0) {
        $('#redirectSecs').text(" "+(--count));
      } else {
        loadDashboard();
      }
    }, 1000);
        }

            }
            catch (e) {
              $.unblockUI();
              $('#errorMsg').text(e.errorResponse + "   Command: " + e.errorCmd);
              $('#errorMsg').show();
              errorLogInConsole(e);
            }


          }, 1000);
          $(this).dialog("close");
        }
      }, {
        text: $.i18n.prop("noStr"),
        click: function() {
          $(this).dialog("close");
        }
      }],
    close: function() {

    }
  });
  $("#redirectNow").click(function() {
    loadDashboard();
  });
  //consoleLogMethodDetailsEnd("wizard.js", "wizardComponent()");

}
$(document).ready(function() {
  //jQuery time
  //configureWizard.loadAndDisplayLanguages();
  $('#ccpWizard').show();
  wizardComponent();
  loadWizardPage();
  $('.fieldsetContent').scroll(function() {
    var scroll = $(this).scrollTop();
    $(this).find('.helpcontent').css('top', scroll);

  });
  $.concat || $.extend({concat: function(b, c) {
      var a = [];
      for (x in arguments){
        a = a.concat(arguments[x]);
      }
      return a;
    }});
  //$(".fieldsetContent").niceScroll();
  //$(".customScroll").slimScroll({ alwaysVisible: true,
  // railVisible: true});
  //configureWizard.configureWizardLoading();

  /*Wizard code ends here*/
  $("#priviewCliPopup").dialog({
    autoOpen: false,
    height: 500,
    width: 720,
    modal: true,
    close: function() {
      $(this).dialog("close");
    }
  });
  /*if($('.helpbody').height()<250){
   $('.helpbody').css("overflow-y","scroll");
   }
   $( window ).resize(function() {
   if($('.helpbody').height()<250){
   $('.helpbody').css("overflow-y","scroll");
   }else{
   $('.helpbody').css("overflow-y","hidden");
   }
   });*/
  $("#checkListDialog").dialog({
    autoOpen: false,
    height: 500,
    width: 700,
    modal: true,
    close: function() {
      $(this).dialog("close");
    }
  });

  $("#previewClip")
    .click(function(e) {
      e.preventDefault();
      // $('#ldapError').hide();
      try {
        //blockPage("Loading");
        $('#previewClip').find('span').text($.i18n.prop("wizardLoading"));
        $('#previewClip').attr("disabled", "disabled");
        previewCli();
        $("#priviewCliPopup").dialog("open");
        $('#previewClip').find('span').text($.i18n.prop("wizardCLI"));
        $('#previewClip').removeAttr("disabled");
      } catch (error) {
        errorLogInConsole(error);
      }
    });
});