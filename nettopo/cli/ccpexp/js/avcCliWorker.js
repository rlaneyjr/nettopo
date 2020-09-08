importScripts("cliWorker.js");
var defineClassMapLimit=74;
onmessage = function (e) {

    jsonObject = JSON.parse(e.data);
    if (jsonObject[0]["name"] == "createPolicy") {
        createPolicy(jsonObject[0]["appList"], jsonObject[0]["sourceZone"], jsonObject[0]["destinationZone"]);
        var cliJson = [{"cliName": "createPolicy","createPolicyStatus": "sucess"}];
        postMessage(JSON.stringify(cliJson));
    } else if (jsonObject[0]["name"] == "getBlockedApps") {
        var allAps = getAllBlockedApplications();
        var cliJson = [{"cliName": "getBlockedApps", "output": allAps}];
        postMessage(JSON.stringify(cliJson));
    } else if (jsonObject[0]["name"] == "exeCli") {
      //  var execli = jsonObject[0]["cli"];
     //   console.log("AVC CLI Worker Receice Messages::"+JSON.stringify(jsonObject));
        var cliNames = jsonObject[0]["cliName"];
        var cliNamesAndCliObj = jsonObject[0]["cliNamesAndCliObj"];
        var resp = getCmdOutputsHandled(cliNames, cliNamesAndCliObj,true);

    } else if (jsonObject[0]["name"] == "writeMemory") {

       getCmdOutputHandled("writeMemory", "write memory", true, false);

    }
};




function getAllBlockedApplications() {
    //consoleLogMethodDetailsWrkrStart("avcCliWorker.js", "getAllBlockedApplications()");
    var allPolicyMap = getPolicyMapWithClasses("", "", false);
    var blockedPolicy = [], appListWithClassName = [];
    //var mergedZoneApps = [];
    if (allPolicyMap.length != 0) {
        for (var j = 0; j < allPolicyMap.length; j++) {
            if (allPolicyMap[j].value.length > 0) {
                var tempBlockPolicy = [];
                for (var i = 0; i < allPolicyMap[j].value.length; i++) {
                    if (allPolicyMap[j].value[i].value == "drop log") {
                        tempBlockPolicy.push(allPolicyMap[j].value[i].name);
                    }
                }
                if (tempBlockPolicy.length > 0) {
                    blockedPolicy.push({name: allPolicyMap[j].name, value: tempBlockPolicy});
                }
            }
        }
    }
    var resp = getCmdOutputHandled("shRunClassMap", "show running-config class-map", true, false);
    var splitResp = resp.split("\n");
    for (var i = 0; i < splitResp.length; i++) {
        var className = "", apps = [];
        if (splitResp[i].indexOf("class-map type inspect match-any") > -1 && splitResp[i].indexOf("_app") > -1) {
            var classNameSplit = splitResp[i].trim().split(/\s+/);
            className = classNameSplit[classNameSplit.length - 1].replace("_app", "");
            for (var j = i + 1; j < splitResp.length; j++) {
                if (splitResp[j].indexOf("match protocol") > -1) {
                    var appSplit = splitResp[j].trim().split(/\s+/);
                    apps.push(appSplit[appSplit.length - 1]);
                } else if (splitResp[j].indexOf("match class-map") > -1 && splitResp[j].indexOf("CATEGORY") > -1) {
                    var categorySplit = splitResp[j].trim().split(/\s+/);
                    var categoryName = categorySplit[categorySplit.length - 1];
                    var categoryTypeSplit = categoryName.trim().split("_");
                    var categoryType = categoryTypeSplit[0] + "_" + categoryTypeSplit[1];
                    for (var k = 0; k < splitResp.length; k++) {
                        if (splitResp[k].indexOf("class-map type inspect match-any") > -1 && splitResp[k].indexOf(categoryType) > -1) {
                            for (var l = k + 1; l < splitResp.length; l++) {
                                if (splitResp[l].indexOf("match protocol") > -1) {
                                    var appSplitMatch = splitResp[l].trim().split(/\s+/);
                                    apps.push(appSplitMatch[appSplitMatch.length - 1]);
                                } else {
                                    break;
                                }
                            }
                        }
                    }
                } else {
                    break;
                }
            }
            appListWithClassName.push({name: className, value: apps});
        }
    }
    //var tempArr = [];
    for (var i = 0; i < blockedPolicy.length; i++) {
        for (var j = 0; j < blockedPolicy[i].value.length; j++) {
            for (var k = 0; k < appListWithClassName.length; k++) {
                if (blockedPolicy[i].value[j] == appListWithClassName[k].name) {
                    blockedPolicy[i].value[j] = {name: appListWithClassName[k].name, value: appListWithClassName[k].value};
                }
            }
        }
    }
    //consoleLogMethodDetailsWrkrEnd("avcCliWorker.js", "getAllBlockedApplications()");
    return blockedPolicy;
}

function getPolicyName(policyMapArr, appListLength) {
    //consoleLogMethodDetailsWrkrStart("avcCliWorker.js", "getPolicyName()");
    var nbarPolicyName = "avc-app-block-";
    var nbarPolicyArr = [], nbarPolicyCount = [], noOfPolicy = 1;
    //var checkExists = false;
    var policyArrWithExist = [];
    if (policyMapArr.length != 0) {
        for (var i = 0; i < policyMapArr[0].value.length; i++) {
            if (policyMapArr[0].value[i].name.indexOf(nbarPolicyName) == 0) {
                nbarPolicyArr.push(nbarPolicyName);
            }
        }
        if (nbarPolicyArr.length > 0) {
            var resp = getCmdOutputHandled("shRunClassMap", "show running-config class-map", true, false);
            var className = "";
            //var spaceFound = false;
            //var policyNumberArr = [], policyNumber = 1;
            var appCount = 0;
            var splitResp = resp.split("\n");
            for (var i = 0; i < splitResp.length; i++) {
                if (splitResp[i].trim().indexOf("class-map type inspect") == 0 && splitResp[i].indexOf(nbarPolicyName) > 0 && splitResp[i].indexOf("_app") > 0) {
                    appCount = 0;
                    var classNameSplit = splitResp[i].trim().split(/\s+/);
                    className = classNameSplit[classNameSplit.length - 1];
                    for (var j = i + 1; j < splitResp.length; j++) {
                        if (splitResp[j].indexOf("match protocol") > -1 || (splitResp[j].indexOf("match class-map") > -1 && splitResp[j].indexOf("CATEGORY") > -1)) {
                            appCount++;
                        } else {
                            break;
                        }
                    }
                    nbarPolicyCount.push({name: className, value: appCount});
                }
            }
            nbarPolicyCount.sort(function (a, b) {
                var splitNumerA = a.name.replace("_app", "").split("-");
                var checkPolicyNumberA = parseInt(splitNumerA[splitNumerA.length - 1]);
                var splitNumerB = a.name.replace("_app", "").split("-");
                var checkPolicyNumberB = parseInt(splitNumerA[splitNumerB.length - 1]);
                if (checkPolicyNumberA < checkPolicyNumberB) {
                    return -1;
        }
                if (checkPolicyNumberA > checkPolicyNumberB) {
                    return 1;
        }
                return 0;
            });
            var tempAppListLength = appListLength;
            for (var i = 0; i < nbarPolicyCount.length; i++) {
                if (nbarPolicyCount[i].value < defineClassMapLimit) {
                    var spaceEmpty = defineClassMapLimit - nbarPolicyCount[i].value;
                    policyArrWithExist.push({policyName: nbarPolicyCount[i].name.replace("_app", ""), exists: true, space: spaceEmpty});
                    tempAppListLength = tempAppListLength - spaceEmpty;
                }
            }
            if (tempAppListLength > 0) {
                var splitNumerA = nbarPolicyCount[nbarPolicyCount.length - 1].name.replace("_app", "").split("-");
                var lastPolicyNumber = parseInt(splitNumerA[splitNumerA.length - 1]);
                policyArrWithExist.push({policyName: nbarPolicyName + (lastPolicyNumber + 1), exists: false, space: defineClassMapLimit});
            }
            /*for(var i=0;i<nbarPolicyCount.length;i++){
             var splitNumer=nbarPolicyCount[i].name.trim().replace("_app","").split("-");
             var checkPolicyNumber=splitNumer[splitNumer.length-1];
             policyNumberArr.push(parseInt(checkPolicyNumber));
             policyNumberArr.sort();
             if (nbarPolicyCount[i].count<74) {
             spaceFound=true;
             nbarPolicyName=nbarPolicyCount[i].name;
             checkExists=true;
             }
             }
             if (!spaceFound) {
             var policyNumberFound=false;
             for(var i=0;i<policyNumberArr.length;i++){
             if (policyNumberArr[i]!=(i+1)) {
             policyNumber=policyNumberArr[i];
             policyNumberFound=true;
             break;
             }
             }
             if (!policyNumberFound) {
             policyNumber=policyNumberArr.length;
             }
             nbarPolicyName=nbarPolicyName+policyNumber;
             }*/

            return policyArrWithExist;
        }else{
             var listLengthModulo = appListLength % defineClassMapLimit;
        var listLengthDivide = Math.floor(appListLength / defineClassMapLimit);
        if (listLengthDivide == 0) {
            if (listLengthModulo > 0) {
                noOfPolicy = 1;
            }
        } else if (listLengthDivide > 0) {
            if (listLengthModulo > 0) {
                noOfPolicy = listLengthDivide + 1;
            } else if (listLengthModulo == 0) {
                noOfPolicy = listLengthDivide;
            }
        }
        //var tempPolicyNameArr = [];
        for (var i = 0; i < noOfPolicy; i++) {
            policyArrWithExist.push({policyName: nbarPolicyName + (i + 1), exists: false, space: defineClassMapLimit});
        }
        return policyArrWithExist;
        }
    } else {
        var listLengthModulo = appListLength % defineClassMapLimit;
        var listLengthDivide = Math.floor(appListLength / defineClassMapLimit);
        if (listLengthDivide == 0) {
            if (listLengthModulo > 0) {
                noOfPolicy = 1;
            }
        } else if (listLengthDivide > 0) {
            if (listLengthModulo > 0) {
                noOfPolicy = listLengthDivide + 1;
            } else if (listLengthModulo == 0) {
                noOfPolicy = listLengthDivide;
            }
        }
        //var tempPolicyNameArr = [];
        for (var i = 0; i < noOfPolicy; i++) {
            policyArrWithExist.push({policyName: nbarPolicyName + (i + 1), exists: false, space: defineClassMapLimit});
        }
        return policyArrWithExist;
    }
    //consoleLogMethodDetailsWrkrEnd("avcCliWorker.js", "getPolicyName()");
    return policyArrWithExist;
}


function createPolicy(appList, sourceZone, destinationZone) {
    //consoleLogMethodDetailsWrkrStart("avcCliWorker.js", "createPolicy()");
    try{
    var policyMapArr = getPolicyMapWithClasses(sourceZone, destinationZone, true);
    var policyNameCheck = getPolicyName(policyMapArr, appList.length);
    if (policyNameCheck.length > 0) {

        for (var j = 0; j < policyNameCheck.length; j++) {
            var policyName = policyNameCheck[j].policyName;
            //defining all CLI's into variable type string
            var objectGrpSrc = "object-group network " + policyName + "_src_net \n any\n";
            var objectGrpDst = "object-group network " + policyName + "_dst_net \n any\n";
            var objectSvc = "object-group service " + policyName + "_svc \n ip\n";
            var accessList = "ip access-list extended " + policyName + "_acl \n permit object-group " + policyName + "_svc object-group " + policyName + "_src_net object-group " + policyName + "_dst_net\n";
            var classMapApp = "class-map type inspect match-any " + policyName + "_app";
            var zonePair = "zone-pair security " + sourceZone + "-" + destinationZone + " source " + sourceZone + " destination " + destinationZone + "\n service-policy type inspect " + sourceZone + "-" + destinationZone + "-POLICY\n";
            var policyMap = "policy-map type inspect " + sourceZone + "-" + destinationZone + "-POLICY\n";
            var matchProtocol = "match protocol ";
            var policyClass = "\nclass-map type inspect match-all " + policyName + "\n match class-map " + policyName + "_app\n match access-group name " + policyName + "_acl\n";
            var appCli = classMapApp;
            var zoneCli = "";
            var classDefault = "class class-default \n drop log\n";
            if (!policyNameCheck[j].exists) {
                for (var i = 0; i < appList.length; i++) {
                    appCli = appCli + "\n" + matchProtocol + appList[i];
                }
                if (policyMapArr.length == 0) {
                    zoneCli = zoneCli + policyMap;
                    zoneCli = zoneCli + "class type inspect " + policyName + " \ndrop log\n";
                    zoneCli = zoneCli + classDefault;
                } else {
                    zoneCli = zoneCli + policyMap;
                    zoneCli = zoneCli + "class type inspect " + policyName + " \ndrop log\n";
                    for (var i = 0; i < policyMapArr[0].value.length; i++) {
                        zoneCli = zoneCli + "class type inspect " + policyMapArr[0].value[i].name + " \n" + policyMapArr[0].value[i].value + "\n";
                    }
                    zoneCli = zoneCli + classDefault;
                }
                zoneCli = zoneCli + zonePair;
                var formCli = objectGrpSrc +
                        objectGrpDst +
                        objectSvc +
                        accessList +
                        appCli +
                        policyClass +
                        zoneCli;
                try {
                    var resp = getCmdOutputHandled("createPolicy", formCli, false, true);
                }
                catch (e) {

                        errorLogInConsole(e);
                }
            }
            else {
                var addAppSize = appList.length;
                if (policyNameCheck[j].space <= appList.length) {
                    addAppSize = policyNameCheck[j].space;
                }
                for (var i = 0; i < addAppSize; i++) {
                    appCli = appCli + "\n" + matchProtocol + appList[i];
                }
                try {
                    var resp = getCmdOutputHandled("createPolicy", appCli, false, true);
                  var trimArray = [];
                    if (policyNameCheck[j].space <= appList) {
                        trimArray = appList.slice(policyNameCheck[j].space, appList.length);
                        appList = trimArray;
                    } else {
                        break;
                    }
                }
                catch (e) {
                        errorLogInConsole(e);
                }
            }
        }
    }
}catch(error){
    errorLogInConsole(error.message);
}
    //consoleLogMethodDetailsWrkrEnd("avcCliWorker.js", "createPolicy()");
}

function getPolicyMapWithClasses(sourceZone, destinationZone, zoneCheck) {
    //consoleLogMethodDetailsWrkrStart("avcCliWorker.js", "getPolicyMapWithClasses()");
    var policyMapArr = [];
    var resp = getCmdOutputHandled("shRunPolicyMap", "show running-config policy-map", true, false);
    var policyMapList = resp.split('policy-map');
    var policyMapNameString = sourceZone + "-" + destinationZone + "-POLICY";
    for (var i = 1; i < policyMapList.length; i++) {
        var policyMapName, className = [];
        var policyLines = policyMapList[i].split("\n");

        for (var j = 0; j < policyLines.length; j++) {
            var splitPolicyLines = policyLines[j].trim().split(/\s+/);
            if (j == 0) {
                policyMapName = splitPolicyLines[splitPolicyLines.length - 1];
            }
            if (policyLines[j].indexOf("class type") > -1) {
                //if (splitPolicyLines[splitPolicyLines.length - 1].trim().toUpperCase() != "INTERNAL_DOMAIN_FILTER") {
                className.push({name: splitPolicyLines[splitPolicyLines.length - 1], value: policyLines[j + 1].trim()});
                //}
            }

        }
        if (zoneCheck) {
            if (policyMapName == policyMapNameString) {
                policyMapArr.push({
                    name: policyMapName,
                    value: className
                });
            }
        } else {
            policyMapArr.push({
                name: policyMapName,
                value: className
            });
        }
    }
    //consoleLogMethodDetailsWrkrEnd("avcCliWorker.js", "getPolicyMapWithClasses()");
    return policyMapArr;
}
