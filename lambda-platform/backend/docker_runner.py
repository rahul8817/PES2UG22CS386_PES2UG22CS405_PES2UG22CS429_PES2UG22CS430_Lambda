import docker
import os
import uuid
import shutil

client = docker.from_env()

def run_function_in_docker(filepath, language, timeout):
    tag = f"lambda-{uuid.uuid4().hex[:6]}"
    filename = os.path.basename(filepath)
    func_dir = os.path.abspath(os.path.dirname(filepath))

    # Copy function to proper name based on language
    extension = "python" if language == "python" else "js"
    new_func_path = f"{func_dir}/function.{extension}"
    shutil.copy(filepath, new_func_path)

    dockerfile = os.path.abspath(f"dockerfiles/{language}.Dockerfile")
    client.images.build(path=func_dir, dockerfile=dockerfile, tag=tag)

    logs = client.containers.run(tag, remove=True, stdout=True, stderr=True, detach=False)
    return logs.decode("utf-8")
