from repositories.attachment_repository import update_attachment, get_attachment

async def process_attachment(attachment_id: str):
    # Stub for virus scan and thumbnail generation
    att = await get_attachment(attachment_id)
    if not att:
        return
    # TODO: call virus scan
    # If image, compute thumbnail and update metadata
    await update_attachment(attachment_id, {"status": "processed"})