$DistDirMin="./__dist_min"
$DistDirRelease="./__dist_release"
$GALogVenvDir="./venv"

Write-Host "Clean GALog venv"
Remove-Item -ErrorAction Continue -Recurse -Path $GALogVenvDir

Write-Host "Clean min dir"
Remove-Item -ErrorAction Continue -Recurse -Path $DistDirMin

Write-Host "Clean release dir"
Remove-Item -ErrorAction Continue -Recurse -Path $DistDirRelease

Write-Host "Done"