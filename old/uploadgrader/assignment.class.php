
<?php /*se assignment class for assignments where you upload a single file
 *
 */
class assignment_uploadgrader extends assignment_base {

	var $filePath;
	var $submissionID;

	function assignment_uploadgrader($cmid='staticonly', $assignment=NULL, $cm=NULL, $course=NULL) {
		parent::assignment_base($cmid, $assignment, $cm, $course);
		$this->type = 'uploadgrader';
	}

	function view() {

		global $USER, $CFG;
		
		$context = get_context_instance(CONTEXT_MODULE,$this->cm->id);

		require_capability('mod/assignment:view', $context);

		add_to_log($this->course->id, "assignment", "view", "view.php?id={$this->cm->id}", $this->assignment->id, $this->cm->id);

		$this->view_header();
		
		$this->view_intro();

		$this->view_dates();

		$filecount = $this->count_user_files($USER->id);

		if ($filecount) {
			$answer_link =  $CFG->wwwroot . '/mod/assignment/type/'.$this->type.'/report.php?uid=' . $USER->id .'&aid='.$this->assignment->id.'&cid='.$this->course->id;
			$output = '<a href="'.$answer_link.'" >See submission</a><br />';
			print_simple_box($output, 'center');
		}

		//call parent get_submission because this class overrides that function
		//if ($submission = parent::get_submission()) {
		//	if ($submission->timemarked) {
		//		$this->view_feedback();
		//	}
		//	if ($filecount) {
				//print_simple_box($this->print_user_files($USER->id, true), 'center');
				//updated by rozi 2012-02-20 13.30
		//		$answer_link =  $CFG->wwwroot . '/mod/assignment/type/'.$this->type.'/report.php?uid=' . $USER->id .'&aid='.$this->assignment->id.'&cid='.$this->course->id;
		//		$output = '<a href="'.$answer_link.'" >See submission</a><br />';				
		//		print_simple_box($output, 'center');
		//	}
		//}

		$isExceed = false;

		if($this->assignment->var1 != 0){
			$isExceed = $filecount >= $this->assignment->var1;
		}

		if (has_capability('mod/assignment:submit', $context)  && $this->isopen() &&
				(!$filecount || $this->assignment->resubmit || !$submission->timemarked)  && !$isExceed) {
			$this->view_upload_form();
		}

		$this->view_footer();
	}

	/**
	 * Fungsi untuk menampilkan intro soal dan deskripsi soal
	 */
	function view_intro() {
		global $CFG, $USER;

		$jsonProbDesc = $CFG->graderPrefix.'problems/' . $this->assignment->description ;

		$probDesc = json_decode(file_get_contents($jsonProbDesc), true);

		$desc = "<b>Title: </b>".$probDesc['title']."<br><b>Description: </b>" .$probDesc['description'] ."<br>";

		print_simple_box_start('center', '', '', 0, 'generalbox', 'intro');
		$formatoptions = new stdClass;
		$formatoptions->noclean = true;
		echo format_text($desc, $this->assignment->format, $formatoptions);

		print_simple_box_end();
	}

	function print_student_answer($userid, $return=false){
		global $CFG, $USER;

		$filearea = $this->file_area_name($userid);

		$output = '';

		if ($basedir = $this->file_area($userid)) {
			if ($files = get_directory_list($basedir)) {
				require_once($CFG->libdir.'/filelib.php');
				foreach ($files as $key => $file) {

					$icon = mimeinfo('icon', $file);
					$ffurl = get_file_url("$filearea/$file");

					$output = '<img src="'.$CFG->pixpath.'/f/'.$icon.'" class="icon" alt="'.$icon.'" />'.
							'<a href="'.$ffurl.'" >'.$file.'</a><br />';
				}
			}
		}

		$output = '<div class="files">'.$output.'</div>';
		return $output;
	}

	function print_student_answer_link($uid, $aid, $cid){
		global $CFG;
		$count = count_records('assignment_submissions', 'assignment', $aid, 'userid', $uid);
		$answer_link =  $CFG->wwwroot . '/mod/assignment/type/'.$this->type.'/report.php?uid=' . $uid .'&aid='.$aid.'&cid='.$cid;
		$output = '<a href="'.$answer_link.'" >See submission for this user...['.$count.']</a><br />';
		return $output;
	}

	/**
	 * Produces a list of links to the files uploaded by a user. Overriding superclass function (taken from assignment_base.php)
	 *
	 * @param $userid int optional id of the user. If 0 then $USER->id is used.
	 * @param $return boolean optional defaults to false. If true the list is returned rather than printed
	 * @return string optional
	 */
	function print_user_files($userid=0, $return=false) {
		global $CFG, $USER;

		if (!$userid) {
			if (!isloggedin()) {
				return '';
			}
			$userid = $USER->id;
		}

		$filearea = $this->file_area_name($userid);

		$output = '';

		if ($basedir = $this->file_area($userid)) {

			$idx = 1;

			//tampilkan semua data yang ada di subdirektori (bila ada)

			if ($files = get_directory_list($basedir, '', false, true)) {
				require_once($CFG->libdir.'/filelib.php');

				foreach ($files as $key => $indir) {
					$file = get_directory_list($basedir . $indir . '/');


					$icon = mimeinfo('icon', $file[0]);
					$ffurl = get_file_url("$filearea/$indir/$file[0]", array('forcedownload'=>1));

					$output .= '<img src="'.$CFG->pixpath.'/f/'.$icon.'" class="icon" alt="'.$icon.'" />'.
							$this->assignment->id." sssss "  .'<a href="'.$ffurl.'" >['.$idx++.']_'.$file[0].'</a></tr><br />';
							
				
							
				}
			}
		}
			//~ $html = "
	//~ <table border='1' cellspacing='2' cellpadding='10' >
	//~ <tr>
	//~ <th class=\"header\" colspan='1'>".$output.""."</th>\n</th><th>dgdydyd</th>
	//~ </table>";		
					//~ echo $html;
		$output = '<div class="files">'.$output .'</div>';

		if ($return) {
			return $output;
		}

		echo $output;
	}

	function view_upload_form() {
		global $CFG;
		$struploadafile = get_string("uploadafile");

		$maxbytes = $this->assignment->maxbytes == 0 ? $this->course->maxbytes : $this->assignment->maxbytes;
		$strmaxsize = get_string('maxsize', '', display_size($maxbytes));

		echo '<div style="text-align:center">';
		echo '<form enctype="multipart/form-data" method="post" '.
				"action=\"$CFG->wwwroot/mod/assignment/upload.php\">";
		echo '<fieldset class="invisiblefieldset">';
		echo "<p>$struploadafile ($strmaxsize)</p>";
		echo '<input type="hidden" name="id" value="'.$this->cm->id.'" />';
		echo '<input type="hidden" name="sesskey" value="'.sesskey().'" />';
		require_once($CFG->libdir.'/uploadlib.php');
		upload_print_form_fragment(1,array('newfile'),false,null,0,$this->assignment->maxbytes,false);
		echo '<input type="submit" name="save" value="'.get_string('uploadthisfile').'" />';
		echo '</fieldset>';
		echo '</form>';
		echo '</div>';
	}


	function upload() {

		global $CFG, $USER;

		require_capability('mod/assignment:submit', get_context_instance(CONTEXT_MODULE, $this->cm->id));

		$this->view_header(get_string('upload'));

		$filecount = $this->count_user_files($USER->id);
		$submission = $this->get_submission($USER->id, true);
		if ($this->isopen() && (!$filecount || $this->assignment->resubmit || !$submission->timemarked)) {

			//bila sebelumnya sudah pernah submit, buat submission baru di database
			//if ($filecount > 0) {
			//	$submission = $this->get_submission($USER->id, true);
			//}

			//buat direktori penyimpanan file di direktori lokal moodle (masih mengikuti peletakan direktori standar moodle)
			$dir = $this->file_area_name($USER->id, $submission->id);
			$dirPath = $CFG->dataroot.'/'.$dir;
			check_dir_exists($dirPath, true, true);

			require_once($CFG->dirroot.'/lib/uploadlib.php');
			$um = new upload_manager('newfile',false,true,$this->course,false,$this->assignment->maxbytes);

			if ($um->process_file_uploads($dir) and confirm_sesskey()) {
				$newfile_name = $um->get_new_filename();

				//mengambil id problem yang akan dikirimkan ke grader
				$assign = get_record('assignment_submissions', 'id', $submission->id, 'userid', $USER->id);
				$assign = get_record('assignment', 'id', $assign->assignment);

				$fileContents = file_get_contents($um->get_new_filepath());

				//menambahkan prefix pada submission id
				$curlSubID = $CFG->subPrefix . $submission->id;

				$result = $this->send_curl($fileContents, $assign->description, $curlSubID, $newfile_name);

				if($result === false){
					$this->clean_up($submission->id, $dirPath);
					notify(get_string("cannotsendtograder", "assignment"));
				}else{
					add_to_log($this->course->id, 'assignment', 'upload',
							'view.php?a='.$this->assignment->id, $this->assignment->id, $this->cm->id);
					$this->update_grade($submission);
					$this->email_teachers($submission);
					print_heading(get_string('uploadedfile'));
				}
			}
			else{
				delete_records('assignment_submissions', 'id', $submission->id);
				notify(get_string("cannotcreatedirectory", "assignment"));
			}

			/*
			if ($um->process_file_uploads($dir) and confirm_sesskey()) {
				$newfile_name = $um->get_new_filename();

				//mengambil id problem yang akan dikirimkan ke grader
				$assign = get_record('assignment_submissions', 'id', $submission->id, 'userid', $USER->id);
				$assign = get_record('assignment', 'id', $assign->assignment);

				//bila baru mau submit pertama kali
				if ($submission && !$filecount) {
					if (update_record("assignment_submissions", $submission)) {

						$fileContents = file_get_contents($um->get_new_filepath());

						//menambahkan prefix pada submission id
						$submission->id = $CFG->subPrefix . $submission->id;

						$result = $this->send_curl($fileContents, $assign->description, $submission->id, $newfile_name);

						// 						$result = true;

						if($result === false){//fail sending to grader, need to cleanup the file and the record in the database
							$this->clean_up($submission->id, $dirPath);
							notify(get_string("cannotsendtograder", "assignment"));
						}else{//success sending to grader
							add_to_log($this->course->id, 'assignment', 'upload',
									'view.php?a='.$this->assignment->id, $this->assignment->id, $this->cm->id);
							$submission = $this->get_submission($USER->id);
							$this->update_grade($submission);
							$this->email_teachers($submission);
							print_heading(get_string('uploadedfile'));
						}
					} else {
						$this->remove_directory($dirPath);
						notify(get_string("uploadfailnoupdate", "assignment"));
					}
				} else {//bila kasusnya adalah mensubmit lagi
					$fileContents = file_get_contents($um->get_new_filepath());

					//menambahkan prefix pada submission id
					$submission->id = $CFG->subPrefix . $submission->id;

					$result = $this->send_curl($fileContents, $assign->description, $submission->id, $newfile_name);

					// 					$result = true;
					//~ $a = json_decode ($result, true);
					//~ if ($a['graded'] === null) { // belum digrade kalo masuk sini
						//~ ...
					//~ } else {
						//~ // udah di-grade
					//~ }

					if($result === false){
						$this->clean_up($submission->id, $dirPath);
						notify(get_string("cannotsendtograder", "assignment"));
					}else{
						add_to_log($this->course->id, 'assignment', 'upload',
								'view.php?a='.$this->assignment->id, $this->assignment->id, $this->cm->id);
						$this->update_grade($submission);
						$this->email_teachers($submission);
						print_heading(get_string('uploadedfile'));
					}
				}
			}
			else{
				delete_records('assignment_submissions', 'id', $submission->id);
				notify(get_string("cannotcreatedirectory", "assignment"));
			}
			*/
		} else {
			notify(get_string("uploaderror", "assignment")); //submitting not allowed!
		}

		print_continue('view.php?id='.$this->cm->id);

		$this->view_footer();
	}

	/**
	 * Function to send_curl request
	 * @param $fileContents the content of the file
	 * @param $pid the problem id
	 * @param $sid the submission id
	 * @param $fileName the name of the file
	 *$CFG mengacu ke file config.php
	 */
	function send_curl($fileContents, $pid, $sid, $fileName){
		global $CFG;
		$ch = curl_init ();
		$fileEncoded = base64_encode ($fileContents);
		$host = $CFG->graderHost;
		$body = json_encode (array (
				'problem' => $pid,
				'answer' => $fileEncoded,
				'filename' => $fileName
		));

		curl_setopt_array ($ch,
				array (
						CURLOPT_CUSTOMREQUEST => 'PUT',
						CURLOPT_URL => $CFG->graderPrefix."submissions/$sid",
						CURLOPT_HTTPHEADER => array (
								'Content-Type: application/json',
								'Content-Length: ' . strlen($body)),
						CURLOPT_POSTFIELDS => $body,
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

	/**
	 * Function to delete data from table and local directory
	 * @param $id the assignment id in the assignment table
	 * @param $dir the directory to be deleted
	 */
	function clean_up($id, $dir){
		delete_records('assignment_submissions', 'id', $id);
		$this->remove_directory($dir);
	}

	/**
	 * Additional function to delete directory. It handles if the directory is not empty.
	 */
	function remove_directory($dir){
		
			//echo $dir;
			foreach (scandir($dir) as $item) {
			if ($item == '.' || $item == '..') continue;
			unlink($dir.DIRECTORY_SEPARATOR.$item);
		}
		rmdir($dir);
	}

	/**
	 * Creates a directory file name, suitable for make_upload_directory(). OVERLOAD parent
	 *
	 * @param $userid int The user id
	 * @return string path to file area
	 */
	function file_area_name($userid, $submissionid) {
		global $CFG;

		return $this->course->id.'/'.$CFG->moddata.'/assignment/'.$this->assignment->id.'/'.$userid.'/'.$submissionid;
	}
	
	/**
	 * Load the submission object for a particular user. OVERRIDE parent
	 *
	 * @param $userid int The id of the user whose submission we want or 0 in which case USER->id is used
	 * @param $createnew boolean optional Defaults to false. If set to true a new submission object will be created in the database
	 * @param bool $teachermodified student submission set if false
	 * @return object The submission
	 */
	function get_submission($userid=0, $createnew=false) {
		global $USER;

		if (empty($userid)) {
			$userid = $USER->id;
		}

		if($createnew){
			$newsubmission = $this->prepare_new_submission($userid, $teachermodified);
			$newid = insert_record("assignment_submissions", $newsubmission);
			if (!$newid) {
				error("Could not insert a new empty submission");
			}

			return get_record('assignment_submissions', 'id', $newid ,'assignment', $this->assignment->id, 'userid', $userid);
		}

		//$submission = get_record('assignment_submissions', 'assignment', $this->assignment->id, 'userid', $userid);

		//if ($submission && !$createnew) {
		//	return $submission;
		//}

		//$newsubmission = $this->prepare_new_submission($userid, $teachermodified);
		//$newid = insert_record("assignment_submissions", $newsubmission);
		//if (!$newid) {
		//	error("Could not insert a new empty submission");
		//}

		//return get_record('assignment_submissions', 'id', $newid ,'assignment', $this->assignment->id, 'userid', $userid);
	}

	/**
	 * Instantiates a new submission object for a given user. OVERRIDE parent
	 *
	 * Sets the assignment, userid and times, everything else is set to default values.
	 * @param $userid int The userid for which we want a submission object
	 * @param bool $teachermodified student submission set if false
	 * @return object The submission
	 */
	function prepare_new_submission($userid, $teachermodified=false) {
		$submission = new Object;
		$submission->assignment   = $this->assignment->id;
		$submission->userid       = $userid;
		$submission->timemodified  = time();
		$submission->timecreated = '';
		$submission->numfiles     = 0;
		$submission->data1        = '';
		$submission->data2        = '';
		$submission->grade        = -1;
		$submission->submissioncomment      = '';
		$submission->format       = 0;
		$submission->teacher      = 0;
		$submission->timemarked   = 0;
		$submission->mailed       = 0;
		return $submission;
	}

	function setup_elements(&$mform) {
		global $CFG, $COURSE;

		$ynoptions = array( 0 => get_string('no'), 1 => get_string('yes'));

		$mform->addElement('select', 'resubmit', get_string("allowresubmit", "assignment"), $ynoptions);
		$mform->setHelpButton('resubmit', array('resubmit', get_string('allowresubmit', 'assignment'), 'assignment'));
		$mform->setDefault('resubmit', 1);

		$mform->addElement('select', 'emailteachers', get_string("emailteachers", "assignment"), $ynoptions);
		$mform->setHelpButton('emailteachers', array('emailteachers', get_string('emailteachers', 'assignment'), 'assignment'));
		$mform->setDefault('emailteachers', 0);

		$choices = get_max_upload_sizes($CFG->maxbytes, $COURSE->maxbytes);
		$choices[0] = get_string('courseuploadlimit') . ' ('.display_size($COURSE->maxbytes).')';
		$mform->addElement('select', 'maxbytes', get_string('maximumsize', 'assignment'), $choices);
		$mform->setDefault('maxbytes', $CFG->assignment_maxbytes);

		$subChoices = array(0 => Unlimited, 5 => 5, 10 => 10, 15 => 15, 20 => 20, 50 => 50, 100 => 100);
		$mform->addElement('select', 'var1', get_string('maximumsubmission', 'assignment'), $subChoices);
		$mform->setDefault('var1', 0);
	}

	function submissions($mode) {
		$this->display_submissions();
	}

	/**
	 *  Display all the submissions ready for grading
	 */
	function display_submissions($message='') {
		global $CFG, $db, $USER;
		require_once($CFG->libdir.'/gradelib.php');

		/* first we check to see if the form has just been submitted
		 * to request user_preference updates
		*/

		if (isset($_POST['updatepref'])){
			$perpage = optional_param('perpage', 10, PARAM_INT);
			$perpage = ($perpage <= 0) ? 10 : $perpage ;
			set_user_preference('assignment_perpage', $perpage);
// 			set_user_preference('assignment_quickgrade', optional_param('quickgrade', 0, PARAM_BOOL));
		}

		/* next we get perpage and quickgrade (allow quick grade) params
		 * from database
		*/
		$perpage    = get_user_preferences('assignment_perpage', 10);

// 		$quickgrade = get_user_preferences('assignment_quickgrade', 0);

		$grading_info = grade_get_grades($this->course->id, 'mod', 'assignment', $this->assignment->id);

		if (!empty($CFG->enableoutcomes) and !empty($grading_info->outcomes)) {
			$uses_outcomes = true;
		} else {
			$uses_outcomes = false;
		}

		$page    = optional_param('page', 0, PARAM_INT);
		$strsaveallfeedback = get_string('saveallfeedback', 'assignment');

		/// Some shortcuts to make the code read better

		$course     = $this->course;
		$assignment = $this->assignment;
		$cm         = $this->cm;

		$tabindex = 1; //tabindex for quick grading tabbing; Not working for dropdowns yet
		add_to_log($course->id, 'assignment', 'view submission', 'submissions.php?id='.$this->cm->id, $this->assignment->id, $this->cm->id);
		$navigation = build_navigation($this->strsubmissions, $this->cm);

		print_header_simple(format_string($this->assignment->name,true), "", $navigation,
				'', '', true, update_module_button($cm->id, $course->id, $this->strassignment), navmenu($course, $cm));

		$course_context = get_context_instance(CONTEXT_COURSE, $course->id);

		if (has_capability('gradereport/grader:view', $course_context) && has_capability('moodle/grade:viewall', $course_context)) {
			echo '<div class="allcoursegrades"><a href="' . $CFG->wwwroot . '/grade/report/grader/index.php?id=' . $course->id . '">'
			. get_string('seeallcoursegrades', 'grades') . '</a></div>';
		}

		if (!empty($message)) {
			echo $message;   // display messages here if any
		}

		$context = get_context_instance(CONTEXT_MODULE, $cm->id);

		/// Check to see if groups are being used in this assignment

		/// find out current groups mode
		$groupmode = groups_get_activity_groupmode($cm);
		$currentgroup = groups_get_activity_group($cm, true);
		groups_print_activity_menu($cm, $CFG->wwwroot . '/mod/assignment/submissions.php?id=' . $this->cm->id);
		if (!empty($CFG->gradebookroles)) {
			$gradebookroles = explode(",", $CFG->gradebookroles);
		} else {
			$gradebookroles = '';
		}

echo "<br><br><br><a href='zipall.php?id=".$this->assignment->id."'>Download All Assignment in ZIP</a>";


		$users = get_role_users($gradebookroles, $context, true, '', 'u.lastname ASC', true, $currentgroup);

		if ($users) {
			$users = array_keys($users);
			if (!empty($CFG->enablegroupings) and $cm->groupmembersonly) {
				$groupingusers = groups_get_grouping_members($cm->groupingid, 'u.id', 'u.id');
				if ($groupingusers) {
					$users = array_intersect($users, array_keys($groupingusers));
				}
			}
		}

// 		$tablecolumns = array('picture', 'fullname', 'grade', 'submissioncomment', 'timemodified', 'timemarked', 'status', 'finalgrade');
		$tablecolumns = array('picture', 'fullname', 'grade', 'submissioncomment', 'timemodified', 'timemarked', 'finalgrade');
		if ($uses_outcomes) {
			$tablecolumns[] = 'outcome'; // no sorting based on outcomes column
		}

		$tableheaders = array('',
				get_string('fullname'),
				get_string('grade'),
				get_string('comment', 'assignment'),
				get_string('lastmodified').' ('.$course->student.')',
				get_string('lastmodified').' ('.$course->teacher.')',
// 				get_string('status'),
				get_string('finalgrade', 'grades'));

		if ($uses_outcomes) {
			$tableheaders[] = get_string('outcome', 'grades');
		}

		require_once($CFG->libdir.'/tablelib.php');
		$table = new flexible_table('mod-assignment-submissions');

		$table->define_columns($tablecolumns);
		$table->define_headers($tableheaders);
		$table->define_baseurl($CFG->wwwroot.'/mod/assignment/submissions.php?id='.$this->cm->id.'&amp;currentgroup='.$currentgroup);

		$table->sortable(true, 'lastname');//sorted by lastname by default
		$table->collapsible(true);
		$table->initialbars(true);

		$table->column_suppress('picture');
		$table->column_suppress('fullname');

		$table->column_class('picture', 'picture');
		$table->column_class('fullname', 'fullname');
		$table->column_class('grade', 'grade');
		$table->column_class('submissioncomment', 'comment');
		$table->column_class('timemodified', 'timemodified');
		$table->column_class('timemarked', 'timemarked');
// 		$table->column_class('status', 'status');
		$table->column_class('finalgrade', 'finalgrade');
		if ($uses_outcomes) {
			$table->column_class('outcome', 'outcome');
		}

		$table->set_attribute('cellspacing', '0');
		$table->set_attribute('id', 'attempts');
		$table->set_attribute('class', 'submissions');
		$table->set_attribute('width', '100%');
		//         $table->set_attribute('align', 'center');

		$table->no_sorting('finalgrade');
		$table->no_sorting('outcome');

		// Start working -- this is necessary as soon as the niceties are over
		$table->setup();

		if (empty($users)) {
			print_heading(get_string('nosubmitusers','assignment'));
			return true;
		}

		/// Construct the SQL

		if ($where = $table->get_sql_where()) {
			$where .= ' AND ';
		}

		if ($sort = $table->get_sql_sort()) {
			$sort = ' ORDER BY '.$sort;
		}

                $gradeQuery = 'SELECT u.id, u.firstname, u.lastname, u.picture, u.imagealt,
		     max(s.id) AS submissionid, s.grade, s.submissioncomment,
		     s.timemodified, s.timemarked,
		     CASE WHEN s.timemarked > 0 AND s.timemarked >= s.timemodified THEN 1
	             ELSE 0 END AS status ';

		$gradeFrom = 'FROM '.$CFG->prefix.'user u '.
				'LEFT JOIN '.$CFG->prefix.'assignment_submissions s ON u.id = s.userid
				AND s.assignment = '.$this->assignment->id.' '.
				'WHERE '.$where.'u.id IN ('.implode(',',$users).') '.
				'GROUP BY u.id';	

		
		$table->pagesize($perpage, count($users));

		///offset used to calculate index of student in that particular query, needed for the pop up to know who's next
		$offset = $page * $perpage;

// 		$strupdate = get_string('update');
// 		$strgrade  = get_string('grade');
		$grademenu = make_grades_menu($this->assignment->grade);

		if (($ausers = get_records_sql($gradeQuery.$gradeFrom.$sort, $table->get_page_start(), $table->get_page_size())) !== false) {

			$grading_info = grade_get_grades($this->course->id, 'mod', 'assignment', $this->assignment->id, array_keys($ausers));

			foreach ($ausers as $auser) {

				$resultgrade = $this->get_curl($auser->submissionid);
				$nilai=json_decode($resultgrade,true);

				$final_grade = $grading_info->items[0]->grades[$auser->id];
				$grademax = $grading_info->items[0]->grademax;
				$final_grade->formatted_grade = round($final_grade->grade,2) .' / ' . round($grademax,2);
				$locked_overridden = 'locked';
				if ($final_grade->overridden) {
					$locked_overridden = 'overridden';
				}

				$picture = print_user_picture($auser, $course->id, $auser->picture, false, true);

				if (empty($auser->submissionid)) {
					$auser->grade = -1; //no submission yet
				}

				if (!empty($auser->submissionid)) {
					///Prints student answer and student modified date
					///attach file or print link to student answer, depending on the type of the assignment.
					///Refer to print_student_answer in inherited classes.
					if ($auser->timemodified > 0) {
						$studentmodified = '<div id="ts'.$auser->id.'">'.$this->print_student_answer_link($auser->id, $this->assignment->id, $this->course->id).'</div>';
					} else {
						$studentmodified = '<div id="ts'.$auser->id.'">&nbsp;</div>';
					}
					///Print grade, dropdown or text
// 					if ($auser->timemarked > 0) {
// 						$teachermodified = '<div id="tt'.$auser->id.'">'.userdate($auser->timemarked).'</div>';

// 						if ($final_grade->locked or $final_grade->overridden) {
// 							$grade = '<div id="g'.$auser->id.'" class="'. $locked_overridden .'">'.$final_grade->formatted_grade.'</div>';
// 						} else if ($quickgrade) {
// 							$menu = choose_from_menu(make_grades_menu($this->assignment->grade),
// 									'menu['.$auser->id.']', $auser->grade,
// 									get_string('nograde'),'',-1,true,false,$tabindex++);
// 							$grade = '<div id="g'.$auser->id.'">'. $menu .'</div>';
// 						} else {
// 							$grade = '<div id="g'.$auser->id.'">'.$this->display_grade($auser->grade).'</div>';
// 						}

// 					} else {
// 						$teachermodified = '<div id="tt'.$auser->id.'">&nbsp;</div>';
// 						if ($final_grade->locked or $final_grade->overridden) {
// 							$grade = '<div id="g'.$auser->id.'" class="'. $locked_overridden .'">'.$final_grade->formatted_grade.'</div>';
// 						} else if ($quickgrade) {
// 							$menu = choose_from_menu(make_grades_menu($this->assignment->grade),
// 									'menu['.$auser->id.']', $auser->grade,
// 									get_string('nograde'),'',-1,true,false,$tabindex++);
// 							$grade = '<div id="g'.$auser->id.'">'.$menu.'</div>';
// 						} else {
// 							$grade = '<div id="g'.$auser->id.'">'.$this->display_grade($auser->grade).'</div>';
// 						}
// 					}
					///Print Comment
					$grade = $nilai['score'];

					if ($final_grade->locked or $final_grade->overridden) {
						$comment = '<div id="com'.$auser->id.'">'.shorten_text(strip_tags($final_grade->str_feedback),15).'</div>';

					} else if ($quickgrade) {
						$comment = '<div id="com'.$auser->id.'">'
						. '<textarea tabindex="'.$tabindex++.'" name="submissioncomment['.$auser->id.']" id="submissioncomment'
						. $auser->id.'" rows="2" cols="20">'.($auser->submissioncomment).'</textarea></div>';
					} else {
						$comment = '<div id="com'.$auser->id.'">'.shorten_text(strip_tags($auser->submissioncomment),15).'</div>';
					}
				} else {
					$studentmodified = '<div id="ts'.$auser->id.'">&nbsp;</div>';
					$teachermodified = '<div id="tt'.$auser->id.'">&nbsp;</div>';
					$status          = '<div id="st'.$auser->id.'">&nbsp;</div>';

					if ($final_grade->locked or $final_grade->overridden) {
						$grade = '<div id="g'.$auser->id.'">'.$final_grade->formatted_grade . '</div>';
					} else if ($quickgrade) {   // allow editing
						$menu = choose_from_menu(make_grades_menu($this->assignment->grade),
								'menu['.$auser->id.']', $auser->grade,
								get_string('nograde'),'',-1,true,false,$tabindex++);
						$grade = '<div id="g'.$auser->id.'">'.$menu.'</div>';
					} else {
						$grade = '<div id="g'.$auser->id.'">-</div>';
					}

					if ($final_grade->locked or $final_grade->overridden) {
						$comment = '<div id="com'.$auser->id.'">'.$final_grade->str_feedback.'</div>';
					} else if ($quickgrade) {
						$comment = '<div id="com'.$auser->id.'">'
						. '<textarea tabindex="'.$tabindex++.'" name="submissioncomment['.$auser->id.']" id="submissioncomment'
						. $auser->id.'" rows="2" cols="20">'.($auser->submissioncomment).'</textarea></div>';
					} else {
						$comment = '<div id="com'.$auser->id.'">&nbsp;</div>';
					}
				}

				if (empty($auser->status)) { /// Confirm we have exclusively 0 or 1
					$auser->status = 0;
				} else {
					$auser->status = 1;
				}

// 				$buttontext = ($auser->status == 1) ? $strupdate : $strgrade;

// 				///No more buttons, we use popups ;-).
// 				$popup_url = '/mod/assignment/submissions.php?id='.$this->cm->id
// 				. '&amp;userid='.$auser->id.'&amp;mode=single'.'&amp;offset='.$offset++;
// 				$button = link_to_popup_window ($popup_url, 'grade'.$auser->id, $buttontext, 600, 780,
// 						$buttontext, 'none', true, 'button'.$auser->id);

// 				$status  = '<div id="up'.$auser->id.'" class="s'.$auser->status.'">'.$button.'</div>';

				$finalgrade = '<span id="finalgrade_'.$auser->id.'">'.$final_grade->str_grade.'</span>';

				$outcomes = '';

				if ($uses_outcomes) {

					foreach($grading_info->outcomes as $n=>$outcome) {
						$outcomes .= '<div class="outcome"><label>'.$outcome->name.'</label>';
						$options = make_grades_menu(-$outcome->scaleid);

						if ($outcome->grades[$auser->id]->locked or !$quickgrade) {
							$options[0] = get_string('nooutcome', 'grades');
							$outcomes .= ': <span id="outcome_'.$n.'_'.$auser->id.'">'.$options[$outcome->grades[$auser->id]->grade].'</span>';
						} else {
							$outcomes .= ' ';
							$outcomes .= choose_from_menu($options, 'outcome_'.$n.'['.$auser->id.']',
									$outcome->grades[$auser->id]->grade, get_string('nooutcome', 'grades'), '', 0, true, false, 0, 'outcome_'.$n.'_'.$auser->id);
						}
						$outcomes .= '</div>';
					}
				}

				$userlink = '<a href="' . $CFG->wwwroot . '/user/view.php?id=' . $auser->id . '&amp;course=' . $course->id . '">' . fullname($auser, has_capability('moodle/site:viewfullnames', $this->context)) . '</a>';
				$row = array($picture, $userlink, $grade, $comment, $studentmodified, $teachermodified, $status, $finalgrade);
				if ($uses_outcomes) {
					$row[] = $outcomes;
				}

				$table->add_data($row);
			}
		}

		/// Print quickgrade form around the table
// 		if ($quickgrade){
// 			echo '<form action="submissions.php" id="fastg" method="post">';
// 			echo '<div>';
// 			echo '<input type="hidden" name="id" value="'.$this->cm->id.'" />';
// 			echo '<input type="hidden" name="mode" value="fastgrade" />';
// 			echo '<input type="hidden" name="page" value="'.$page.'" />';
// 			echo '<input type="hidden" name="sesskey" value="'.sesskey().'" />';
// 			echo '</div>';
// 		}

		$table->print_html();  /// Print the whole table

// 		if ($quickgrade){
// 			$lastmailinfo = get_user_preferences('assignment_mailinfo', 1) ? 'checked="checked"' : '';
// 			echo '<div class="fgcontrols">';
// 			echo '<div class="emailnotification">';
// 			echo '<label for="mailinfo">'.get_string('enableemailnotification','assignment').'</label>';
// 			echo '<input type="hidden" name="mailinfo" value="0" />';
// 			echo '<input type="checkbox" id="mailinfo" name="mailinfo" value="1" '.$lastmailinfo.' />';
// 			helpbutton('emailnotification', get_string('enableemailnotification', 'assignment'), 'assignment').'</p></div>';
// 			echo '</div>';
// 			echo '<div class="fastgbutton"><input type="submit" name="fastg" value="'.get_string('saveallfeedback', 'assignment').'" /></div>';
// 			echo '</div>';
// 			echo '</form>';
// 		}
		/// End of fast grading form

		/// Mini form for setting user preference
		echo '<div class="qgprefs">';
		echo '<form id="options" action="submissions.php?id='.$this->cm->id.'" method="post"><div>';
		echo '<input type="hidden" name="updatepref" value="1" />';
		echo '<table id="optiontable">';
		echo '<tr><td>';
		echo '<label for="perpage">'.get_string('pagesize','assignment').'</label>';
		echo '</td>';
		echo '<td>';
		echo '<input type="text" id="perpage" name="perpage" size="1" value="'.$perpage.'" />';
		helpbutton('pagesize', get_string('pagesize','assignment'), 'assignment');
		echo '</td></tr>';
// 		echo '<tr><td>';
// 		echo '<label for="quickgrade">'.get_string('quickgrade','assignment').'</label>';
// 		echo '</td>';
// 		echo '<td>';
// 		$checked = $quickgrade ? 'checked="checked"' : '';
// 		echo '<input type="checkbox" id="quickgrade" name="quickgrade" value="1" '.$checked.' />';
// 		helpbutton('quickgrade', get_string('quickgrade', 'assignment'), 'assignment').'</p></div>';
// 		echo '</td></tr>';
		echo '<tr><td colspan="2">';
		echo '<input type="submit" value="'.get_string('savepreferences').'" />';
		echo '</td></tr></table>';
		echo '</div></form></div>';
		///End of mini form

                $data = array();
		$data[0] = $this->course->id;
		$data[1] = $this->assignment->id;
		$data[2] = $this->course->shortname;
		$data[3] = $this->assignment->name;
		$data[4] = $currentgroup;

                //array_push($users, $this->assignment->id);
		//array_push($users, $this->course->shortname);
		//array_push($users, $this->assignment->name);
		$link = $CFG->wwwroot.'/mod/assignment/type/uploadgrader/exportexcel.php';
		print_single_button($link,
				$data, get_string('download', 'admin'));						
		echo '</div>';

		print_footer($this->course);
	}


//echo "<br><br><br><a href='zipall.php?id=".$this->assignment->id."'>Download All Assignment in ZIP</a>";




//penambahan 

	/*
	 * Counts all real assignment submissions by ENROLLED students (not empty ones)
	 *
	 * @param $groupid int optional If nonzero then count is restricted to this group
	 * @return int The number of submissions
	 */
	function count_real_submissions($groupid=0) {
		return count_distinct_submission($this->cm, $groupid);
	}

	function get_curl($subid ){
		global $CFG;
		$ch = curl_init ();
	
		curl_setopt_array ($ch,
				array (
						CURLOPT_CUSTOMREQUEST => 'GET',
						CURLOPT_URL => $CFG->graderPrefix."submissions/fasilkom12$subid",
						CURLOPT_FAILONERROR => true,
						CURLOPT_BINARYTRANSFER => true,
						CURLOPT_RETURNTRANSFER => true
				));
	
		$result = curl_exec ($ch);
	
		curl_close ($ch);
	
		return $result;
	}
}

function count_distinct_submission($cm, $groupid=0) {
	global $CFG;

	$context = get_context_instance(CONTEXT_MODULE, $cm->id);

	if (!empty($CFG->gradebookroles)) {
		$gradebookroles = explode(",", $CFG->gradebookroles);
	} else {
		$gradebookroles = '';
	}

	$users = get_role_users($gradebookroles, $context, true, '', 'u.lastname ASC', true, $groupid);

	if ($users) {
		$users = array_keys($users);
		// if groupmembersonly used, remove users who are not in any group
		if (!empty($CFG->enablegroupings) and $cm->groupmembersonly) {
			$groupingusers = groups_get_grouping_members($cm->groupingid, 'u.id', 'u.id');
			if ($groupingusers) {
				$users = array_intersect($users, array_keys($groupingusers));
			}
		}
	}

	if (empty($users)) {
		return 0;
	}

	$userlists = implode(',', $users);

	return count_records_sql("SELECT COUNT(*) FROM (
			select distinct userid
			from scl_assignment_submissions as T
			where assignment = $cm->instance AND timemodified > 0 AND userid IN ($userlists)
			) as T");
}

?>

