<?php
date_default_timezone_set('America/New_York');
?>
<html>
<head>
<title>PHP ENCRYPTION DECRYPTION MYSQL | The Best PHP Encryption Tutorial</title>
<link href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css" rel="stylesheet" type="text/css" >
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/animate.css/3.5.2/animate.min.css">
</head>
<body>
<div class="jumbotron"><h1>The Best PHP Encryption Tutorial</h1></div>
<div class="container">
<div class="row">
<div class="col-sm-3"></div>
<div class="col-sm-6">
<?php
//THE KEY FOR ENCRYPTION AND DECRYPTION
$key = 'qkwjdiw239&&jdafweihbrhnan&^%$ggdnawhd4njshjwuuO';
//ENCRYPT FUNCTION
function encryptthis($data, $key) {
$encryption_key = base64_decode($key);
$iv = openssl_random_pseudo_bytes(openssl_cipher_iv_length('aes-256-cbc'));
$encrypted = openssl_encrypt($data, 'aes-256-cbc', $encryption_key, 0, $iv);
return base64_encode($encrypted . '::' . $iv);
}
//DECRYPT FUNCTION
function decryptthis($data, $key) {
$encryption_key = base64_decode($key);
list($encrypted_data, $iv) = array_pad(explode('::', base64_decode($data), 2),2,null);
return openssl_decrypt($encrypted_data, 'aes-256-cbc', $encryption_key, 0, $iv);
}
 
if(isset($_POST['submit'])){
 
//GET POST VARIABLES
$firstName=$_POST['firstName'];
$email=$_POST['email'];
 
//THE ENCRYPTION PROCESS
$nameencrypted=encryptthis($firstName, $key);
$emailencrypted=encryptthis($email, $key);
 
//THE DECRYPTION PROCESS
$namedecrypted=decryptthis($nameencrypted, $key);
$emaildecrypted=decryptthis($emailencrypted, $key);
 
//DISPLAY RESULTS
echo '<h2>Original Data</h2>';
echo '<p>Name: '.$firstName.'</p>';
echo '<p>Email: '.$email.'</p>';
echo '<h2>Encrypted Data</h2>';
echo '<p>Name Encrypted: </p><p style="background-color:yellow">'.$nameencrypted.'</p>';
echo '<p>Email Encrypted: </p><p style="background-color:yellow; word-break: break-all;">'.$emailencrypted.'</p>';
echo '<h2>Decrypted Data</h2>';
echo '<p>Name Decrypted: '.$namedecrypted.'</p>';
echo '<p>Email Decrypted: '.$emaildecrypted.'</p>';
echo '<h2>Insert Results Into Database</h2>';
echo '<p>We will insert the encrypoted information into the database with this code.</p>'; ?>
<pre> mysqli_query($con,"INSERT INTO people(`name`, `email`)
VALUES ('$nameencrypted','$emailencrypted')");</pre>
 
<h2>Retreieve Results From Database</h2>
<p>We will retrieve the results from the database with this code;</p>
<pre>
$con = new mysqli("$host", "$username", "$password", "$dbname");
$result = $con->query("SELECT * FROM people") ;
while ($row = $result->fetch_assoc()) {
echo decryptthis($row['name'], $key);
echo decryptthis($row['email'], $key);
}
</pre>
<?php
}
 
//SEPERATOR
echo '<div class="well"><h2>Our Form</h2>';
 
//FORM FOR OUR EXAMPLE
echo '<form method="post">
<div class="form-group">
<label for="firstName">Enter Name Here</label>
<input type="text" class="form-conrtol" name="firstName">
</div>
<div class="form-group">
<label for="email">Enter Email Here</label>
<input type="email" class="form-conrtol" name="email">
</div>
<input type="submit" name="submit" class="btn btn-success btn-lg" value="submit">
</form>';
?>
</div>
</div>
<div class="col-sm-3"></div>
</div>
</div>
</body>
</html>
