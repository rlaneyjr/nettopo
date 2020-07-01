Export-NpsConfiguration -Path C:\TEMP\LocalNPSExportedConfig.xml

$CurrentServerNPS = $env:computername

$NPServers = Get-ADGroupMember "RAS and IAS Servers"
$NPServers | ForEach-Object {

	$NPServerName = $_.Name

	if ($NPServerName -ne $CurrentServerNPS) {
		$NPServerName
		Export-NpsConfiguration -Path \\$NPServerName\C$\TEMP\LocalNPSExportedConfig.xml
		Invoke-Command -ComputerName $NPServerName -ScriptBlock {Export-NPSConfiguration -Path C:\TEMP\BackupNPSExportedConfig.xml
		Invoke-Command -ComputerName $NPServerName -ScriptBlock {Import-NPSConfiguration -Path C:\TEMP\LocalNPSExportedConfig.xml
	}

}
