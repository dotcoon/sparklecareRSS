import yaml
import certifi

# Determine the path to cacert.pem
cacert_path = certifi.where()

# Load existing YAML configuration
with open(".github/workflows/update_comic.yml", "r") as yaml_file:
    config = yaml.safe_load(yaml_file)

# Update relevant field in YAML configuration
config["jobs"]["update_comic"]["steps"].insert(3, {
    "name": "Set REQUESTS_CA_BUNDLE",
    "run": f"echo 'export REQUESTS_CA_BUNDLE={cacert_path}' >> $GITHUB_ENV"
})

# Save modified YAML configuration back to file
with open(".github/workflows/update_comic.yml", "w") as yaml_file:
    yaml.dump(config, yaml_file)