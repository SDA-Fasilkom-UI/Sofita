


<?php
require_once("../../config.php");
    require_once("lib.php");
 
    $id = optional_param('id', 0, PARAM_INT);  // Assignment ID

// masih dalam tahap pengembangan empty masih salah
    if (!empty($course->id)) {
        error("Only teachers can look at this page");
    }

    if (!$assignment = get_record("assignment", "id", $id)) {
        error("Course module is incorrect");
    }

    if (! $course = get_record("course", "id", $assignment->course)) {
        error("Course is misconfigured");
    }

    require_login($course->id);
    //echo $CFG->dataroot."/".$course->id."/moddata/assignment/".$id;
    //echo "<br>";
    //echo $CFG->dataroot."/".$course->id."/assignment-".$id.".zip";
    zip_files(array($CFG->dataroot."/".$course->id."/moddata/assignment/".$id),$CFG->dataroot."/".$course->id."/assignment-".$id.".zip");
    header("Location: ".$CFG->wwwroot."/file.php/".$course->id."/assignment-".$id.".zip");
?>

