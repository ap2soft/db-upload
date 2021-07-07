<?php
error_reporting(0);


$host = "http://io.dbwap.ru/";
$tmp_folder = "tmp/";
$target_folder = "upload/";
      $db = @mysql_connect ("localhost","dbwap","aszx12");
	if(!$db){exit('ERR##Извините, но MySQL сервер временно не доступен. Зайдите позже.');}
	$dd=@mysql_select_db("db",$db);
      include"../dbwap.ru/config.php";
# для тестирование через браузер без использования клиентской программы
//if (@$_GET['test']==1) { $_POST=$_GET; }

if(isset($_GET['del']) or isset($_POST['del']) and isset($_GET['file']) or isset($_POST['file'])){
if(isset($_GET['del']) and isset($_GET['file'])){
$del=$_GET['del'];
$filov=$_GET['file'];}else{
$del=$_POST['del'];
$filov=$_POST['file'];
}
$nnn = mysql_fetch_array(mysql_query("SELECT * FROM rand WHERE n='$filov'",$db));
$ff = $nnn['md5'];
if($nnn['del'] == $del){
$deleted = 1;}else{$deleted = 0;}
if($deleted==1){
mysql_query("DELETE FROM rand WHERE n='$filov'");
unlink("../dbwap.ru/storage/".$ff);
echo "DEL##OK";exit();
} else {
echo "DEL##ERR##Невозможно удалить ссылку!";exit();}}

@$tmp_file_name=$tmp_folder.'part_'.$_POST['file_hash'].'.tmp';

#test log
//$xxx = fopen("test.log","a");
//fputs($xxx,sprintf("filename=%s, flag=%s, size=%s\n",$_POST['filename'],$_POST['flag'],$_POST['file_send']));
//fclose($xxx);
##test log

if (@$_POST['flag']=='upload_start') {
  # получен сигнал о НАЧАЛЕ закачки
  if (is_file($tmp_file_name.".ini")) {
    # файл уже существует - подаём сигнал о докачке, начиная с $size байт
    
    #$file_info = file($tmp_file_name.".ini");
    $size = filesize($tmp_file_name);
    echo "RETR##$size";
#test log
//$xxx = fopen("test.log","a");
//fputs($xxx,"RETR##$size\n");
//fclose($xxx);
##test log
    exit();
  }
  else {
    # файла ещё нет - создаём его и подаём сигнал о докачке, начиная с 0 байт
    $file_info = explode("::::",str_replace("\n"," ",str_replace("\r","",base64_decode($_POST['file_info']))));
    $file_info[] = 0;
    $f=fopen($tmp_file_name.".ini",'w');
    foreach ($file_info as $ln) { fputs($f, $ln."\n"); }
    fclose($f);
    echo "RETR##0";
#test log
//$xxx = fopen("test.log","a");
//fputs($xxx,"RETR##0\n");
//fclose($xxx);
##test log
    
    #if (file_exists($tmp_file_name)) { unlink($tmp_file_name); }
    exit();
  }
}
elseif (@$_POST['flag']=='upload_continue' || @$_POST['flag']=='upload_finish') {
  # получен сигнал о ПРОДОЛЖЕНИИ закачки или об ОТПРАВКЕ ПОСЛЕДНЕГО КУСКА

  # делаем запись в ini
  if (!is_file($tmp_file_name.".ini")) {
    echo "ERR##Файл ini не найден! [$tmp_file_name.ini]";
    exit();
  }
  # сохраняем полученный кусок
  if (isset($_POST['part']) && isset($_POST['file_send'])) {
    $file_info = file($tmp_file_name.".ini");
    $file_info[sizeof($file_info)-1]=$_POST['file_send'];
    $f=fopen($tmp_file_name.".ini",'w');
    foreach ($file_info as $ln) { fputs($f, str_replace("\n","",$ln)."\n"); }
    fclose($f);

    $f=fopen($tmp_file_name,'ab');
    fputs($f,base64_decode($_POST['part']));
    fclose($f);

    # получен сигнал об ОКОНЧАНИИ закачки
    if ($_POST['flag']=='upload_finish') {
      # проверяем целостность
      $f=fopen($tmp_file_name,'rb');
      $file_hash = md5(fread($f, filesize($tmp_file_name)));
      fclose($f);
      if ($file_hash != $_POST['file_hash']) {
        echo "ERR##MD5-хэш не совпадает!";
#test log
//$xxx = fopen("test.log","a");
//fputs($xxx,"ERR##MD5-хэш не совпадает!\n");
//fclose($xxx);
##test log
        exit();
      }

      $new_filename = end(explode("\\",$_POST['filename']));
      rename($tmp_file_name, $target_folder.$new_filename);
      rename($tmp_file_name.".ini", $target_folder.$new_filename.".ini");
#test log
//$xxx = fopen("test.log","a");
//fputs($xxx,"rename success\n");
//fclose($xxx);
##test log
      
      $file_check='upload/'.$new_filename;
      $file_c_name=$new_filename;
      include "../dbwap.ru/antivirus.php";
      if($avir==0){
      echo 'ERR##Файл заражен вирусом!\n'.$vir[0];
      unlink('upload/'.$new_filename);
      include("./footer.php");
     die();
     }

      $r = rand(000001,999999);
      $s = rand(100000, 999999);
      if (isset($_SERVER['HTTP_X_FORWARDED_FOR']) && preg_match("|^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$|", $_SERVER['HTTP_X_FORWARDED_FOR'])){
      $ip = $_SERVER['HTTP_X_FORWARDED_FOR'];}
      elseif(isset($_SERVER['HTTP_CLIENT_IP']) && preg_match("|^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$|", $_SERVER['HTTP_CLIENT_IP'])) {
      $ip = $_SERVER['HTTP_CLIENT_IP'];}
      else {$ip = preg_replace("|[^0-9.]|", "", $_SERVER['REMOTE_ADDR']);}
      $time = time();
      
      $description = checks(str_replace("\n"," ",str_replace("\r","",   str_replace("Описание файла","",
$file_info[0]))));
      
      $cat = '';
      
      /* сделал замену переводов строк на ничто */
      $passwerd = checks(str_replace("\n","",str_replace("\r","",$file_info[2])));
      $name = checks($new_filename);
      $mime = end(explode(".", $name));
      $mime = strtolower($mime); 

      $size = $file_info[3] / 1048576;
      $maxfilesize = 15;
      if($size > $maxfilesize) {
        echo "ERR##Файл слишком большой!";
#test log
//$xxx = fopen("test.log","a");
//fputs($xxx,"ERR##Файл слишком большой!\n");
//fclose($xxx);
##test log
        exit();
      }
      if(mysql_num_rows(mysql_query("SELECT id FROM rand WHERE md5='$file_hash'",$db))>0) {
        echo "ERR##Файл уже существует!";
#test log
//$xxx = fopen("test.log","a");
//fputs($xxx,"ERR##Файл уже существует!\n");
//fclose($xxx);
##test log
        exit();
      }


      $passs = md5($passwerd);
      $result = mysql_query ("INSERT INTO rand (md5,n,name,del,ip,down,time,about,pass,mime,moded) VALUES ('$file_hash','$r','$name','$s','$ip','0','$time','$description','$passs','$mime','1')") or die(mysql_error());
      
      if($mime=='jpg' or $mime=='gif' or $mime=='png'){
require ('../dbwap.ru/class/thumb.php');
img_resize('upload/'.$new_filename, '../dbwap.ru/preview/'.$r.'_preview.jpg', 100, 60);
}
      $movefile = "../dbwap.ru/storage/" . $file_hash;
      copy('upload/'.$new_filename, $movefile);

      unlink('upload/'.$new_filename);
      unlink('upload/'.$new_filename.'.ini');
      
      # подаём сигнал об успешной загрузке
      echo "OK##http://dbwap.ru/$r/$s";
#test log
//$xxx = fopen("test.log","a");
//fputs($xxx,"OK##http://dbwap.ru/$r/$s\n");
//fclose($xxx);
##test log
      exit();
    }
    else {
      echo "RETR##".filesize($tmp_file_name);
#test log
//$xxx = fopen("test.log","a");
//fputs($xxx,"RETR##".filesize($tmp_file_name)."\n");
//fclose($xxx);
##test log
      exit();
    }
  }
  else {
    echo "ERR##Не задан параметр part!";
#test log
//$xxx = fopen("test.log","a");
//fputs($xxx,"ERR##Не задан параметр part!\n");
//fclose($xxx);
##test log
    exit();
  }
}
echo "ERR##Wrong params!";
?>