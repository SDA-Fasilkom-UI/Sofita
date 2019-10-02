<?php

require_once('../../../../config.php');
require_once($CFG->libdir . '/filelib.php');
require_once($CFG->libdir . '/adminlib.php');
require_once($CFG->libdir . '/setuplib.php');
require_once($CFG->libdir.'/gradelib.php');
require_once($CFG->dirroot.'/grade/lib.php');
require_once($CFG->dirroot.'/grade/report/user/lib.php');

require_once($CFG->dirroot . '/grade/report/lib.php');
require_once($CFG->libdir.'/tablelib.php');

$userid = required_param('uid', PARAM_INT);
$assignmentid = required_param('aid', PARAM_INT);
$courseid = required_param('cid', PARAM_INT);

/// basic access checks
if (!$user = get_record('user', 'id', $userid)) {
	// 	print_error('nocourseid');
	print_error('nouserid');
}

if (!$course = get_record('course', 'id', $courseid)) {
	// 	print_error('nocourseid');
	print_error('nocourseid');
}

if (!$assignment = get_record('assignment_submissions', 'assignment', $assignmentid)) {
	// 	print_error('nocourseid');
	print_error('noassignmentid');
}

require_login($course);

$context = get_context_instance(CONTEXT_COURSE, $course->id);
require_capability('gradereport/user:view', $context);

$access = false;
if (has_capability('moodle/grade:viewall', $context)) {
	//ok - can view all course grades
	$access = true;

} else if ($userid == $USER->id and has_capability('moodle/grade:view', $context) and $course->showgrades) {
	//ok - can view own grades
	$access = true;

} else if (has_capability('moodle/grade:viewall', get_context_instance(CONTEXT_USER, $userid)) and $course->showgrades) {
	// ok - can view grades of this user- parent most probably
	$access = true;
}

if (!$access) {
	// no access to grades!
	error("Can not view grades.", $CFG->wwwroot.'/course/view.php?id='.$courseid);
}

$query = "SELECT * FROM scl_assignment_submissions WHERE  assignment = " . $assignmentid . " AND userid = " . $userid . " ORDER BY id DESC";

$res = get_records_sql($query);

$name = $user->firstname . ' ' . $user->lastname;

print_grade_page_header($courseid, 'report', 'user', get_string('modulename', 'gradereport_user'). ' - '.$name);

echo '<br />'.print_table_grader($courseid, $assignmentid, $userid, $res, true);

//messy? don't ask me
//--------------------------------------------------------//

/**
 * Hacking print_grade_page_head function. Only take what is needed.
 */
function print_grade_page_header($courseid, $active_type, $active_plugin=null, $heading = false, $return=false, $bodytags='', $buttons=false, $extracss=array()) {
	global $CFG, $COURSE;

	$navlinks = array();

	$navlinks[] = array('name' => 'Grades',
			'link' => $null,
			'type' => 'misc');

	$navlinks[] = array('name' => 'View',
			'link' => $null,
			'type' => 'misc');

	$navlinks[] = array('name' => 'User Report',
			'link' => $null,
			'type' => 'misc');

	$navigation = build_navigation($navlinks);

	$returnval = print_header_simple($strgrades . ': ' . $stractive_type, $title, $navigation, '',
			$bodytags, true, $buttons, navmenu($COURSE), false, '', $return);

	// Guest header if not given explicitly
	if (!$heading) {
		$heading = $stractive_plugin;
	}

	if ($CFG->grade_navmethod == GRADE_NAVMETHOD_COMBO || $CFG->grade_navmethod == GRADE_NAVMETHOD_DROPDOWN) {
		$returnval .= print_grade_plugin_selector($plugin_info, $return);
	}
	$returnval .= print_heading($heading);

	if ($return) {
		return $returnval;
	}
}

/**
 * Hacking print_table function. Modified as desired
 */
function print_table_grader($cid, $aid, $uid, $resultset, $return=false) {
	/*
	 * Modified by Rozi on 2012-02-21 08.50
	* Change the header for student role
	*/
	global $COURSE, $USER, $SESSION;
	$isStudent = false;

	// 	$context = get_context_instance(CONTEXT_COURSE,$COURSE->id);

	// 	if (has_capability('moodle/legacy:student', $context, $USER->id, false) ) {
	//$isStudent = true;
	// 	}
	// 	if (has_capability('moodle/legacy:teacher', $context, $USER->id, false) ) {
	// 		echo "is Teaching Assistant<br/>";
	// 	}
	// 	if (has_capability('moodle/legacy:editingteacher', $context, $USER->id, false)) {
	// 		echo "is Teacher<br/>";
	// 	}
	// 	if (has_capability('moodle/legacy:admin', $context, $USER->id, false)) {
	// 		echo "is Admin<br/>";
	// 	}

	//for now this part will be used
	$context = get_context_instance(CONTEXT_COURSE,$SESSION->cal_course_referer);

	if ($roles = get_user_roles($context, $USER->id)) {
		foreach ($roles as $role) {
			if($role->name === 'Student'){
				$isStudent = true;
				break;
			}
		}
	}

	if($isStudent)
		$header = array(0 => 'Submission', 'File', 'Submit Time', 'Grade', 'Comment');
	else
		$header = array(0 => 'ID', 'File', 'Submit Time', 'Grade', 'Comment');

	$column = array(0 => 'timemodified', 'grade', 'timemarked');
	$class = 'item b1b';

	$maxspan = 2;
	$colspan = $maxspan;

	/// Build table structure
	$html = "
	<table border='1' cellspacing='2' cellpadding='10' class='boxaligncenter generaltable user-grade'>
	<thead>
	<tr>
	<th class=\"header\" colspan='1'>".$header[0]."</th>\n";

	for ($i = 1; $i < count($header); $i++) {
		$html .= "<th class=\"header\">".$header[$i]."</th>\n";
	}

	$html .= "
	</tr>
	</thead>
	<tbody>\n";

	// print out the table data

	$idx = 1;
	foreach ($resultset as $subid => $row){
		$resultgrade = send_curls($subid);
		$nilai=json_decode($resultgrade,true);

		$html .= "<tr>\n";

		//if student, don't show the id number. it might confuse them
		if($isStudent)
			$html .= "<td class='$class' $colspan align='center'>".$idx++."</td>\n";
		else
			$html .= "<td class='$class' $colspan align='center'>".$subid."</td>\n";

		// 		$html .= "<td class='$class' $colspan>".$subid."</td>\n";
		$html .= "<td class='$class' $colspan>".print_user_files($cid, $aid, $uid, $subid)."</td>\n";
		//for($j = 0; $j < count($column); $j++){
		//$colname = $column[$j];
		//jika
		//print_r($colname);
		//~ if($colname == 'timemodified' || $colname == 'timemarked'){
		//~ $time = 'not marked yet';
		//~ if($row->$colname ||$nilai['graded']!==null ){
		//~ $time = date("Y-m-d H:i:s", $row->$colname);
		//~ //$time = $nilai['graded'];// date("Y-m-d H:i:s", $nilai['graded']);
		//~ }
		//~ $html .= "<td class='$class' $colspan>".$time."</td>\n";
		//~ }else{
		//~ if ($nilai['graded']===null){
		//~ $html .= "<td class='$class' $colspan>". $row->$colname."</td>\n";
		//~ }
		//~ else{
		//~ $html .= "<td class='$class' $colspan>". $nilai['score']."</td>\n";
		//~ }
		//~ }
			
			
		//~ //jika ada waktu submisiin maka kasih aja selain itu kosogn, jika ada nilai grade maka kasih aja selain itu kosong, jika ada waktu grade maka kasih aja selain tu kosong
			
		if ($subid){
			$time = date("Y-m-d H:i:s", $row->timemodified);
			$html .= "<td class='$class' $colspan>". $time."</td>\n";
		}
			
		if ($nilai['graded']===null){
			$html .= "<td class='$class' $colspan>". "-"."</td>\n";
		}
		else{
			$html .= "<td class='$class' $colspan>". $nilai['score']."</td>\n";
		}
			
			
		if ($nilai['graded']===null){
			$html .= "<td class='$class' $colspan>". "not marked yet"."</td>\n";
		}
		else{
			$text = "";
			if($nilai['compile-status'] !== 'ok'){
				$text = "Compile error";
			}

$ks = array_keys ($nilai['results']);
sort ($ks);
foreach ($ks as $tc)
{
	$atc = $nilai['results'][$tc];
	$v = $atc['verdict'];
	$rt = $atc['running-time'];
	$text .= "$tc: $v: $rt<br>";
}
				
			$html .= "<td class='$class' $colspan>".$text."</td>\n";
			//ga jadi dipake
				
			//menghapus tanda | karena terlihat sedikit aneh
			//waktu server dalam UTC/GMT, harus diubah ke waktu lokal
			//$localTime = new DateTime ($nilai['graded']);
			//$localTime->modify("+7 hour");
			//$html .= "<td class='$class' $colspan>". $localTime->format("Y-m-d H:i:s")."</td>\n";
			//$html .= "<td class='$class' $colspan>"." | ". $nilai['graded']."</td>\n";
		}
			
			
			
			
		//}
		$html .= "</tr>\n";
	}

	$html .= "</tbody></table>";

	if ($return) {
		return $html;
	} else {
		echo $html;
	}
}

function print_user_files($cid, $aid, $uid, $sid) {
	global $CFG;

	$filearea = $cid.'/'.$CFG->moddata.'/assignment/'.$aid.'/'.$uid.'/'.$sid;


	$output = '';

	if ($basedir = make_upload_directory($filearea)) {
		if ($files = get_directory_list($basedir, '', false, true)) {
			$ffurl = get_file_url("$filearea/$files[0]", array('forcedownload'=>1));
			$output .= '<a href="'.$ffurl.'" >'.$files[0].'</a><br />';
		}
	}

	$output = '<div class="files">'.$output.'</div>';

	return $output;
}

function send_curls($subid ){
	global $CFG;
	$ch = curl_init ();
	//$fileEncoded = base64_encode ($fileContents);
	//$host = $CFG->graderHost;
	//~ $body = json_encode (array (
	//~ 'problem' => $pid,
	//~ 'answer' => $fileEncoded,
	//~ 'filename' => $fileName
	//~ ));

	curl_setopt_array ($ch,
			array (
					CURLOPT_CUSTOMREQUEST => 'GET',
					CURLOPT_URL => $CFG->graderPrefix.'submissions/'.$CFG->subPrefix.$subid,
					//~ CURLOPT_HTTPHEADER => array (
					//~ 'Content-Type: application/json',
					//~ 'Content-Length: ' . strlen($body)),
					//~ CURLOPT_POSTFIELDS => $body,
					CURLOPT_FAILONERROR => true,
					CURLOPT_BINARYTRANSFER => true,
					CURLOPT_RETURNTRANSFER => true
			));

	$result = curl_exec ($ch);

	//get the submission status
	// 		$status = curl_getinfo($ch, CURLINFO_HTTP_CODE);

	curl_close ($ch);

	return $result;
}

?>

