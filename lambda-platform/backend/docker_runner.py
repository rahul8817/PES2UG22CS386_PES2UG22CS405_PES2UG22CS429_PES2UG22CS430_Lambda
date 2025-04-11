import docker
import os
import uuid
import shutil

client = docker.from_env()

def run_function_in_docker(filepath, language, timeout):
    ext = {
        "python": "python",
        "javascript": "javascript"
    }

    if language not in ext:
        return f"Unsupported language: {language}"

    # Unique tag and copy path
    tag = f"lambda-func-{uuid.uuid4().hex[:6]}"
    filename = f"function.{ext[language]}"
    workdir = os.path.dirname(filepath)
    dest_path = os.path.join(workdir, filename)

    shutil.copy(filepath, dest_path)

    dockerfile_path = f"dockerfiles/{language}.Dockerfile"

    try:
        image, _ = client.images.build(path=workdir, dockerfile=os.path.abspath(dockerfile_path), tag=tag)

        container = client.containers.run(
            image=image.id,
            detach=True,
            name=tag,
            stdout=True,
            stderr=True
        )

        try:
            result = container.wait(timeout=timeout)
            logs = container.logs().decode()
        except Exception:
            container.kill()
            logs = "⏱️ Execution timed out."
        finally:
            container.remove()

    except Exception as e:
        logs = f"❌ Error: {str(e)}"

    # Clean up copied file
    if os.path.exists(dest_path):
        os.remove(dest_path)

    return logs
