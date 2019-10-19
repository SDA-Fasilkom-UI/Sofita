<?php

require_once '../../../../config.php';
require_once $CFG->dirroot.'/grade/export/lib.php';

send_to_excel($_GET);

function send_to_excel($data){
	global $CFG, $db, $USER;
	require_once($CFG->libdir.'/gradelib.php');
	require_once($CFG->dirroot.'/lib/excellib.class.php');

	$cid = $data[0];
	$aid = $data[1];
	$sname = $data[2];
	$aname = $data[3];
	$group = $data[4];

	
	if($group){
		$groupquery = 'SELECT g.userid FROM '.$CFG->prefix.'groups_members g , '.$CFG->prefix.'role_assignments r WHERE g.groupid = '. $group . ' AND g.userid = r.userid AND r.roleid = 5' ;
		$uidingroup = array();
		$i = 0;

		$usersingroup = get_records_sql($groupquery);

		foreach($usersingroup as $key => $val){
			$uidingroup[$i++] = $val->userid;
		}
	}else{
//		$idquery = 'SELECT u.id FROM ' .$CFG->prefix. 'user u, '.$CFG->prefix.'role_assignments r WHERE u.id = r.userid AND r.roleid = 5';
$idquery = 'SELECT u.id FROM ' .$CFG->prefix. 'user u, '.$CFG->prefix.'role_assignments r, '.$CFG->prefix.'assignment_submissions s WHERE u.id = r.userid AND r.roleid = 5 AND u.id = s.userid AND s.assignment = '.$aid;



		$ids = get_records_sql($idquery);
		$uidingroup = array();
		$i = 0;

		foreach($ids as $key => $val){
			$uidingroup[$i++] = $val->id;
		}
	}
	
	$gradeQuery = 'SELECT u.id, u.firstname, u.lastname, u.idnumber, u.username, s.grade, max(s.id) AS submissionid ';

	$gradeFrom = 'FROM '.$CFG->prefix.'user u '.
			'LEFT JOIN '.$CFG->prefix.'assignment_submissions s ON u.id = s.userid
			AND s.assignment = '.$aid.' '.
			'WHERE '.$where.'u.id IN ('.implode(',',$uidingroup).') '.
			'GROUP BY u.id';	

	
	if (($ausers = get_records_sql($gradeQuery.$gradeFrom)) !== false) {
		foreach ($ausers as $auser) {		
			$auser->grade = '-';
			if(!empty($auser->submissionid)){
				$resultgrade = send_curls($auser->submissionid);
				$nilai = json_decode($resultgrade,true);
				$auser->grade = $nilai['score'];
			}	

			$uldap = search_ldap($auser->username);								
			//$npm = search_ldap($auser->username,1);
			if($uldap[1] !== false){
				$auser->idnumber = $uldap[1];
			}
			
			//$name = search_ldap($auser->username,0);
			if($uldap[0] !== false){
				$auser->firstname = $uldap[0];								
			}else{
				$name = $auser->firstname .' '.$auser->lastname;
				$auser->firstname = $name;
			}						
		}
							
		$downloadfilename = $sname ."_Grades_".$aname;

		$workbook = new MoodleExcelWorkbook("-");
		$workbook->send($downloadfilename);

		$myxls =& $workbook->add_worksheet("Grades");

		$myxls->write_string(0,0,"NPM");
		$myxls->write_string(0,1,"Name");
		$myxls->write_string(0,2,$aname);
		
		$i = 1;
		foreach ($ausers as $auser) {			
			$myxls->write_string($i,0,$auser->idnumber);
			$myxls->write_string($i,1,$auser->firstname);
			$myxls->write_string($i,2,$auser->grade);
			$i++;
		}

		$workbook->close();
	}
	exit;
}

function send_curls($subid ){
	global $CFG;
	$ch = curl_init ();

	curl_setopt_array ($ch,
			array (
					CURLOPT_CUSTOMREQUEST => 'GET',
					CURLOPT_URL => $CFG->graderPrefix."submissions/".$CFG->subPrefix.$subid,
					CURLOPT_FAILONERROR => true,
					CURLOPT_BINARYTRANSFER => true,
					CURLOPT_RETURNTRANSFER => true
			));

	$result = curl_exec ($ch);

	curl_close ($ch);

	return $result;
}

function search_ldap($username_mhs){

	$ds=ldap_connect("account.ui.ac.id");  // must be a valid LDAP server!

	$query=$username_mhs;

	if ($ds&&$query) {
		$r=ldap_bind($ds);     // this is an "anonymous" bind, typically
		// read-only access

		//~ echo "Mencari '$query' ...<br/>";
		// Search surname entry
		$sr=ldap_search($ds, "ou=Mahasiswa,ou=Users,ou=Fakultas Ilmu Komputer,o=Universitas Indonesia,c=ID", "mail=*".$query."*");

		//~ echo "Ditemukan " . ldap_count_entries($ds, $sr) . " hasil<br/>";

		$info = ldap_get_entries($ds, $sr);

		//~ echo "<table border=1>";
		//~ echo "<tr><th>NAMA</th><th>NPM</th><th>Email</th></tr>";

		//~ for ($i=0; $i<$info["count"]; $i++) {
		//~ echo "<tr><td>" . $info[$i]["gecos"][0] . "</td><td>".$info[$i]["kodeidentitas"][0]."</td><td>" . $info[$i]["mail"][0] . "</td></tr>";

		//~ }
		//~ echo "</table>";

		//$info[$i]["kodeidentitas"][0];
		$p= explode("-", $info[0]["gecos"][0]);
                $p[0] = strtoupper($p[0]);
		//if ($kolom==0) return  strtoupper($p[0]) ;
		//else if($kolom==1) return  $p[1] ;

		return $p;

		ldap_close($ds);
	}
}

?>
