
# Cloudflare Gateway Adblock

Automatic add gatway lists and rules to Cloudflare

Every day at 2PM Update blocked domain list and upload to Gateway

In create-upload.py edit to your block list location, will get in worflow logs below python script
## TNX for code

- [@X-rays5](https://github.com/X-rays5/cloudflare_adblock)
- [JamesWoolfenden](https://github.com/JamesWoolfenden/terraform-cloudflare-adblock)

## Add secrets
```
    CF_API_ACCOUNT_ID (can be get by account-id.py)

    CF_API_EMAIL (your email)

    CF_API_TOKEN (your api token)

    LIST_FNAME_SECRET (name of blocked domain txt file)

    LIST_URLS_SECRET (Blocked lists separete by new line)
