resource "aws_dynamodb_table" "dynamodb-table-pets" {
  name           = "MusiciansWithPets"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "Title"
  range_key      = "Pet"

  stream_enabled   = true
  stream_view_type = "NEW_AND_OLD_IMAGES"

  attribute {
    name = "Title"
    type = "S"
  }

  attribute {
    name = "Pet"
    type = "S"
  }


  tags = {
    Name        = "dynamodb-pet-table"
    Environment = "tutorial"
  }
}



resource "aws_dynamodb_table" "tunes" {
  name           = "popsongs"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "Artist"
  range_key      = "Title-version"


  attribute {
    name = "Artist"
    type = "S"
  }

  attribute {
    name = "Title-version"
    type = "S"
  }


  tags = {
    Name        = "dynamodb-tune-table"
    Environment = "tutorial"
  }
}
