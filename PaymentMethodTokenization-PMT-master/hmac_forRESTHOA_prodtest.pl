#! /usr/bin/perl
use Digest::SHA qw(hmac_sha256_hex hmac_sha512_hex);

my $private_key = 'VINDICA_PROVIDES_THIS_KEY';
my $token = KHPApril12T2;
my $one_time_token = "$token#POST#/payment_methods";
my $signed_one_time_token = hmac_sha256_hex($one_time_token, $private_key);
print "Token: $token\nFull Token Value: $one_time_token\nSigned: $signed_one_time_token\n";


