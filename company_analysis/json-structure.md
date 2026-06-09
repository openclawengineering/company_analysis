## Company info aggregate JSON fields:

- company_folder_name

- company_name_en

- company_name_jp

- company_domains (fields, list)

- products_and_services (list of objects)
  - name

  - type [product / service]

  - client_type [b2b / b2c]

  - description

  - target_demography

- company_profile
  - address

  - phone

  - fax

  - founded (year and month)

  - established (year and month)

  - capital

  - num_of_employees

  - sales (list of objects)
    - date_type [year / quarter / range]

    - date (based on date_type)

    - total sales

- people (list of objects)
  - name_en

  - name_jp

  - title (designation)

  - notes

  - linkedin (object)
    - profile_available (if person has linkedin profile url)

    - data_available (if data has been successfully scraped)

    - url

    - [other linkedin profile fields]

  - twitter_url
    - profile_available (if person has twitter profile url)

    - data_available (if data has been successfully scraped)

    - url

    - [other twitter profile fields]

- partners (list of names)

- certifications (list of certification names)

- links (list of objects)
  - name_and_description

  - url

tech_stack (list of tech names)
