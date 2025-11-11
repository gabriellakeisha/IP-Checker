<?php
echo "Test Script Starting\n";
require('functions.inc.php');

$t="there are four words";
$expect=4;

$answer=wordcount($t);

echo "Test Result: '".$t."'=".$answer." (expected: ".$expect.")\n";

if ($answer==$expect)
{
    echo "Test Passed\n";
    exit(0); // exit code 0 - success
}
else
{
    echo "Test Failed\n";
    exit(1); // exit code not zero - error
}
