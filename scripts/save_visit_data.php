<?php
/**
* Copyright 2012, SDSC
* UCSD, San Diego, CA 92093
*
* @author Jeff Sale
* @version 1.0
* @package insert_jump_events.php
*
* This file saves event data when user clicks a 'Jump' button to 
* jump to an search string instance in the transcription
*  
**/


/////////////////////////////////////////////////////////////////////////////////////////////////////////
// Insert date and time stamp for patient viewing education information.
/////////////////////////////////////////////////////////////////////////////////////////////////////////
$datevar = date('Y-m-d');
$timevar = date('H:i:s');

if (!isset($_POST['uid']) || !isset($_POST['session_id']) || !isset($_POST['search_string'])) {
	
	$error_string = "There was a problem with your submission. Please contact the system administrator at admin@education.sdsc.edu with questions.<br />";
	exit();
	
} else {
	$uid = $_POST['uid'];
	$session_idvar = $_POST['session_id'];
	$search_string = $_POST['search_string'];
	
	function curPageURL() {
		$pageURL = 'http';
		if ($_SERVER["HTTPS"] == "on") {$pageURL .= "s";}
		$pageURL .= "://";
		if ($_SERVER["SERVER_PORT"] != "80") {
		$pageURL .= $_SERVER["SERVER_NAME"].":".$_SERVER["SERVER_PORT"].$_SERVER["REQUEST_URI"];
		} else {
		$pageURL .= $_SERVER["SERVER_NAME"].$_SERVER["REQUEST_URI"];
		}
		return $pageURL;
	}
	$string = curPageURL();

	$DEBUG = false;
	$mydrupaluid = 1;
	$session_idvar = 123;
	
	if (isset($_POST['search_string'])) {
		$search_string = strip_tags($_POST['search_string']);
		$search_string = htmlentities($search_string);
	
		$size_of_captions = sizeof($captions);
		if ($DEBUG) echo "size_of_captions: $size_of_captions<br/>";
		for ($i = 0; $i < $size_of_captions; $i++) {
			if (preg_match("/".$search_string."/", strtolower($captions[$i]))) {
				$minutes = abs(round(($caption_times[$i]-30)/60));
				$minute_seconds = abs($minutes * 60);
				$remainder_seconds = $caption_times[$i] - $minute_seconds;
				if ($remainder_seconds < 10) {
					$remainder_string = "0".$remainder_seconds;
				} else {
					$remainder_string = "$remainder_seconds";
				}
				$time_string = $minutes.":".$remainder_string;
				$caption_words = explode(" ", $captions[$i]);
				$caption_string = "";
				for ($j = 0; $j < 6; $j++) {
					$caption_string .= $caption_words[$j]." ";
				}
				echo '<b><a onClick="jumpto('.$caption_times[$i].','.$mydrupaluid.',\''.$session_idvar.'\',\''.$search_string.'\')" onmouseover="" style="cursor: pointer;">Jump to '.$time_string.' - "'.$caption_string.'..."</a></b><br>';
			}
		}
		$fpout = fopen('log.txt','a');
		$remote_address = $_SERVER['REMOTE_ADDR'];
		$datevar = date('Y_m_d_h_i_s');
		$outputstring = $datevar.",".$remote_address.",".$search_string."\n";
		fwrite($fpout, $outputstring);
		fclose($fpout);
	}
}

?>
